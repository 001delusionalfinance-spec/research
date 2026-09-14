"""Ingestion des courbes souveraines G10 restantes -- Canada, Australie, Suede.

Complete `ingestion_souverains_quotidiens.py` (zone euro, Royaume-Uni, Japon). Avec ces trois
pays, la couverture quotidienne des courbes passe de 4 a 7 blocs. Chaque source est la banque
centrale nationale elle-meme, verifiee en direct le 2026-09-14.

- **Canada** -- API Valet de la Banque du Canada. Le groupe `bond_yields_benchmark` expose
  d'un coup 2/3/5/7/10 ans et le long terme. Note : les identifiants de serie ne se devinent
  pas (V39055 et consorts, essayes en premier, renvoient une erreur) -- il faut passer par
  l'endpoint de GROUPE, qui liste lui-meme ses series.
- **Australie** -- table statistique F2 de la Reserve Bank of Australia, en CSV. Le fichier a
  huit lignes d'en-tete descriptives avant les donnees ; la ligne utile est celle qui commence
  par "Series ID", et c'est elle qui donne la correspondance colonne -> maturite. Meme piege
  que le fichier du MOF japonais : on la cherche par son libelle, jamais par un indice en dur.
- **Suede** -- API SWEA de la Riksbank, une serie par maturite (SEGVB2YC, 5Y, 7Y, 10Y).

Non retenus, testes le meme jour :
- **Nouvelle-Zelande** : la RBNZ renvoie HTTP 403 sur ses fichiers statistiques (acces
  automatise bloque). Courbe NZ toujours absente.
- **Norvege** : l'API de la Norges Bank repond pour le taux directeur mais le chemin des
  rendements souverains testé renvoie 404 ; jeu correct non identifie a ce stade.
- **Suisse** : le portail de la SNB repond, mais le cube de rendements quotidiens renvoie une
  derniere observation a 2025-07 -- soit un gel, soit un tri du fichier qui n'est pas
  chronologique. Non tranche, donc non ingere plutot qu'ingere a l'aveugle.

Usage :
    python ingestion_souverains_g10.py
"""

import csv
import io
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BRUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "souverains"

BOC_URL = ("https://www.bankofcanada.ca/valet/observations/group/bond_yields_benchmark/json"
           "?start_date=1990-01-01")
BOC_MATURITES = {
    "BD.CDN.2YR.DQ.YLD": "CANADA_2A",
    "BD.CDN.5YR.DQ.YLD": "CANADA_5A",
    "BD.CDN.10YR.DQ.YLD": "CANADA_10A",
    "BD.CDN.LONG.DQ.YLD": "CANADA_LONG",
}

RBA_URL = "https://www.rba.gov.au/statistics/tables/csv/f2-data.csv"
RBA_MATURITES = {
    "FCMYGBAG2D": "AUSTRALIE_2A",
    "FCMYGBAG5D": "AUSTRALIE_5A",
    "FCMYGBAG10D": "AUSTRALIE_10A",
}

RIKSBANK_URL = "https://api.riksbank.se/swea/v1/Observations/{serie}/1990-01-01"
RIKSBANK_SERIES = {
    "SEGVB2YC": "SUEDE_2A",
    "SEGVB5YC": "SUEDE_5A",
    "SEGVB10YC": "SUEDE_10A",
}

MIN_LIGNES = 100
MAX_JOURS_RETARD = 15


def _http(url: str, accept: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": accept})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _valider(points: list, nom: str) -> None:
    if len(points) < MIN_LIGNES:
        raise ValueError(f"seulement {len(points)} ligne(s) pour {nom} -- snapshot degrade")
    derniere = datetime.strptime(points[-1][0], "%Y-%m-%d").date()
    retard = (datetime.now(timezone.utc).date() - derniere).days
    if retard > MAX_JOURS_RETARD:
        raise ValueError(f"derniere donnee du {points[-1][0]} pour {nom} -- {retard} jours de "
                         f"retard (seuil {MAX_JOURS_RETARD})")
    # Pas de controle de signe : un rendement souverain peut etre negatif.


def _ecrire(nom: str, points: list) -> None:
    BRUT_DIR.mkdir(parents=True, exist_ok=True)
    chemin = BRUT_DIR / f"{nom}.csv"
    with chemin.open("w", encoding="utf-8") as f:
        f.write("date,taux\n")
        for jour, valeur in points:
            f.write(f"{jour},{valeur:.6f}\n")
    print(f"{nom} : {len(points)} lignes (jusqu'a {points[-1][0]}) -> {chemin}")


def ingerer_canada() -> list:
    try:
        charge = json.loads(_http(BOC_URL, "application/json"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"CANADA : echec -- {e}")
        return [("CANADA", str(e))]

    series = {nom: [] for nom in BOC_MATURITES.values()}
    for observation in charge.get("observations", []):
        jour = observation.get("d")
        if not jour:
            continue
        for cle, nom in BOC_MATURITES.items():
            cellule = observation.get(cle) or {}
            brut = cellule.get("v")
            if brut in (None, ""):
                continue
            series[nom].append((jour, float(brut)))

    echecs = []
    for nom, points in series.items():
        try:
            points.sort()
            _valider(points, nom)
            _ecrire(nom, points)
        except ValueError as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
    return echecs


def ingerer_australie() -> list:
    try:
        texte = _http(RBA_URL, "text/csv")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"AUSTRALIE : echec -- {e}")
        return [("AUSTRALIE", str(e))]

    lignes = [r for r in csv.reader(io.StringIO(texte)) if r]
    # Huit lignes descriptives precedent les donnees. La correspondance colonne -> maturite est
    # portee par la ligne "Series ID" : on la cherche par son libelle, jamais par un indice en
    # dur (meme precaution que pour le fichier du MOF japonais).
    index_ids = next((i for i, r in enumerate(lignes[:20])
                      if r and r[0].strip().lower() == "series id"), None)
    if index_ids is None:
        print("AUSTRALIE : echec -- ligne 'Series ID' introuvable")
        return [("AUSTRALIE", "entete introuvable")]

    ids = [c.strip() for c in lignes[index_ids]]
    colonnes = {ids.index(code): nom for code, nom in RBA_MATURITES.items() if code in ids}
    if not colonnes:
        print(f"AUSTRALIE : echec -- aucune maturite attendue dans {ids[:6]}")
        return [("AUSTRALIE", "maturites absentes")]

    series = {nom: [] for nom in colonnes.values()}
    for ligne in lignes[index_ids + 1:]:
        if not ligne or not ligne[0].strip():
            continue
        try:
            jour = datetime.strptime(ligne[0].strip(), "%d-%b-%Y").date().isoformat()
        except ValueError:
            continue
        for position, nom in colonnes.items():
            if position >= len(ligne):
                continue
            brut = ligne[position].strip()
            if not brut:
                continue
            try:
                series[nom].append((jour, float(brut)))
            except ValueError:
                continue

    echecs = []
    for nom, points in series.items():
        try:
            points.sort()
            _valider(points, nom)
            _ecrire(nom, points)
        except ValueError as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
    return echecs


def ingerer_suede() -> list:
    echecs = []
    for serie, nom in RIKSBANK_SERIES.items():
        try:
            charge = json.loads(_http(RIKSBANK_URL.format(serie=serie), "application/json"))
            points = sorted((o["date"], float(o["value"])) for o in charge
                            if o.get("value") is not None)
            _valider(points, nom)
            _ecrire(nom, points)
        except (ValueError, KeyError, TypeError, urllib.error.URLError,
                urllib.error.HTTPError, TimeoutError) as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
    return echecs


def main() -> int:
    print("=== Canada (Banque du Canada) ===")
    echecs = ingerer_canada()
    print("\n=== Australie (Reserve Bank of Australia) ===")
    echecs += ingerer_australie()
    print("\n=== Suede (Riksbank) ===")
    echecs += ingerer_suede()

    total = len(BOC_MATURITES) + len(RBA_MATURITES) + len(RIKSBANK_SERIES)
    if echecs:
        print(f"\n{len(echecs)}/{total} courbes en echec : {[n for n, _ in echecs]}")
        return 1
    print(f"\nOK -- {total} courbes souveraines G10 ingerees")
    return 0


if __name__ == "__main__":
    sys.exit(main())
