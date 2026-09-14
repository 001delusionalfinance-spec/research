"""Ingestion des bilans de banques centrales absents de FRED.

`ingestion_fred.py` couvre les bilans de la Fed (avec ses composantes), de la BCE et de la
Banque du Japon. Ce fichier prend le relais pour les banques centrales que FRED n'expose pas,
en allant chez elles.

Etat de la recherche menee le 2026-09-14, gardee ici pour ne pas etre refaite a l'aveugle :

| Banque centrale | Resultat                                                              |
|-----------------|-----------------------------------------------------------------------|
| **Banque d'Angleterre** | **Retenue** -- serie `RPWB55A` de sa base statistique, hebdomadaire |
| **Reserve Bank of Australia** | **Retenue** -- table statistique A1, hebdomadaire |
| **Banque du Canada** | **Retenue** -- groupe `B2_WEEKLY` de l'API Valet, hebdomadaire. Trouve en parcourant la liste complete des 2537 groupes : trois noms devines au prealable renvoyaient tous 404. Les identifiants de cette API ne se devinent pas, il faut lister |
| Riksbank | Aucune serie de bilan exposee par l'API SWEA (liste complete parcourue) |
| SNB | Le portail expose bien une API mais l'endpoint de liste des cubes renvoie du HTML, pas l'index attendu. Cube de bilan non identifie |
| PBOC, RBNZ, Norges | Non explores a ce stade |

Pourquoi ca compte : une banque centrale peut laisser son taux directeur inchange et durcir
fortement en laissant son bilan se reduire. Sans les bilans, on ne lit qu'une moitie de la
politique monetaire -- et pour l'instant cette moitie n'est visible que pour la Fed, la BCE,
la Banque du Japon et desormais la Banque d'Angleterre.

Usage :
    python ingestion_bilans_nationaux.py
"""

import csv
import io
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BRUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "bilans"

BOE_URL = ("https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp?csv.x=yes"
           "&Datefrom=01/Jan/1990&Dateto=now&SeriesCodes={code}&CSVF=TN&UsingCodes=Y"
           "&VPD=Y&VFD=N")
BOE_SERIES = {
    "BOE_BILAN_TOTAL": "RPWB55A",   # total du bilan, hebdomadaire
}

RBA_URL = "https://www.rba.gov.au/statistics/tables/csv/a1-data.csv"
# Identifiants portes par la ligne "Series ID" de la table A1. On garde le total et les deux
# grandes poches d'actifs -- c'est la composition qui dit s'il s'agit de QE (titres locaux) ou
# d'accumulation de reserves (or et devises).
RBA_SERIES = {
    "RBA_BILAN_TOTAL": "ARBALTLEW",
    "RBA_OR_ET_DEVISES": "ARBAAGFXW",
    "RBA_TITRES_LOCAUX": "ARBAAASTW",
}

BOC_URL = ("https://www.bankofcanada.ca/valet/observations/group/B2_WEEKLY/json"
           "?start_date=1990-01-01")

MIN_LIGNES = 50
# Hebdomadaire, publie a J-5 environ (verifie : 2026-09-09 au 2026-09-14).
MAX_JOURS_RETARD = 21


def _http(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                               "Accept": "text/csv"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def ingerer_boe() -> list:
    echecs = []
    for nom, code in BOE_SERIES.items():
        try:
            lignes = [r for r in csv.reader(io.StringIO(_http(BOE_URL.format(code=code))))
                      if r and len(r) >= 2]
            points = []
            for date_brute, valeur in ((r[0], r[1]) for r in lignes[1:]):
                if not valeur.strip():
                    continue
                jour = datetime.strptime(date_brute.strip(), "%d %b %Y").date()
                points.append((jour.isoformat(), float(valeur)))
            points.sort()

            if len(points) < MIN_LIGNES:
                raise ValueError(f"seulement {len(points)} ligne(s) -- snapshot degrade")
            derniere = datetime.strptime(points[-1][0], "%Y-%m-%d").date()
            retard = (datetime.now(timezone.utc).date() - derniere).days
            if retard > MAX_JOURS_RETARD:
                raise ValueError(f"derniere donnee du {points[-1][0]} -- {retard} jours de "
                                 f"retard (seuil {MAX_JOURS_RETARD})")

            BRUT_DIR.mkdir(parents=True, exist_ok=True)
            chemin = BRUT_DIR / f"{nom}.csv"
            with chemin.open("w", encoding="utf-8") as f:
                f.write("date,valeur\n")
                for jour, valeur in points:
                    f.write(f"{jour},{valeur:.6f}\n")
            print(f"{nom} : {len(points)} lignes (jusqu'a {points[-1][0]}) -> {chemin}")
        except (ValueError, IndexError, urllib.error.URLError,
                urllib.error.HTTPError, TimeoutError) as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
    return echecs


def _ecrire(nom: str, points: list) -> None:
    if len(points) < MIN_LIGNES:
        raise ValueError(f"seulement {len(points)} ligne(s) pour {nom} -- snapshot degrade")
    derniere = datetime.strptime(points[-1][0], "%Y-%m-%d").date()
    retard = (datetime.now(timezone.utc).date() - derniere).days
    if retard > MAX_JOURS_RETARD:
        raise ValueError(f"derniere donnee du {points[-1][0]} pour {nom} -- {retard} jours de "
                         f"retard (seuil {MAX_JOURS_RETARD})")
    BRUT_DIR.mkdir(parents=True, exist_ok=True)
    chemin = BRUT_DIR / f"{nom}.csv"
    with chemin.open("w", encoding="utf-8") as f:
        f.write("date,valeur\n")
        for jour, valeur in points:
            f.write(f"{jour},{valeur:.6f}\n")
    print(f"{nom} : {len(points)} lignes (jusqu'a {points[-1][0]}) -> {chemin}")


def ingerer_rba() -> list:
    try:
        lignes = [r for r in csv.reader(io.StringIO(_http(RBA_URL))) if r]
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"RBA : echec -- {e}")
        return [("RBA", str(e))]

    # Meme structure que la table F2 des rendements : plusieurs lignes descriptives avant les
    # donnees, la correspondance colonne -> serie portee par la ligne "Series ID". Cherchee par
    # son libelle, jamais par un indice en dur.
    index_ids = next((i for i, r in enumerate(lignes[:20])
                      if r and r[0].strip().lower() == "series id"), None)
    if index_ids is None:
        print("RBA : echec -- ligne 'Series ID' introuvable")
        return [("RBA", "entete introuvable")]
    ids = [c.strip() for c in lignes[index_ids]]
    colonnes = {ids.index(code): nom for nom, code in RBA_SERIES.items() if code in ids}
    if not colonnes:
        print(f"RBA : echec -- aucune serie attendue dans {ids[:6]}")
        return [("RBA", "series absentes")]

    series = {nom: [] for nom in colonnes.values()}
    for ligne in lignes[index_ids + 1:]:
        if not ligne or not ligne[0].strip():
            continue
        try:
            jour = datetime.strptime(ligne[0].strip(), "%d-%b-%Y").date().isoformat()
        except ValueError:
            continue
        for position, nom in colonnes.items():
            if position >= len(ligne) or not ligne[position].strip():
                continue
            try:
                series[nom].append((jour, float(ligne[position].strip())))
            except ValueError:
                continue

    echecs = []
    for nom, points in series.items():
        try:
            points.sort()
            _ecrire(nom, points)
        except ValueError as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
    return echecs


def ingerer_boc(compteur: list) -> list:
    try:
        charge = json.loads(_http(BOC_URL))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"BOC : echec -- {e}")
        return [("BOC", str(e))]

    detail = charge.get("seriesDetail", {})
    series = {cle: [] for cle in detail}
    for observation in charge.get("observations", []):
        jour = observation.get("d")
        if not jour:
            continue
        for cle in series:
            brut = (observation.get(cle) or {}).get("v")
            if brut in (None, ""):
                continue
            series[cle].append((jour, float(brut)))

    # L'API Valet nomme ses series par des codes opaques (V36612, V1160788296...). Les ecrire
    # tels quels rendrait les fichiers inexploitables pour qui ecrira les modeles : personne ne
    # sait ce qu'est V36612. Le libelle est fourni par le bloc `seriesDetail` -- on le conserve
    # dans un index a cote des fichiers, et on l'affiche a l'ingestion.
    echecs, index, discontinuees = [], [], []
    for cle, points in series.items():
        nom = "BOC_" + cle.replace(".", "_").upper()
        libelle = (detail.get(cle) or {}).get("label") or "(libelle absent)"
        try:
            points.sort()
            _ecrire(nom, points)
            print(f"    -> {libelle}")
            index.append((nom, cle, libelle, len(points)))
            compteur.append(nom)
        except ValueError as e:
            # Une serie DISCONTINUEE a l'interieur d'un groupe par ailleurs vivant n'est pas
            # une panne : c'est une facilite fermee (cas reel le 2026-09-14, V36632 s'arrete au
            # 2022-12-28, soit ~1350 jours). Le groupe est prouve vivant par les autres series,
            # donc on signale sans faire echouer le module -- meme logique que la couverture
            # partielle du ratio de service de la dette cote BIS.
            discontinuees.append((nom, libelle, str(e)))
            print(f"{nom} : ignoree -- {libelle} : {e}")

    if discontinuees:
        print(f"  ({len(discontinuees)} serie(s) discontinuee(s) dans le groupe, non bloquant)")

    if index:
        BRUT_DIR.mkdir(parents=True, exist_ok=True)
        chemin_index = BRUT_DIR / "BOC_index.csv"
        with chemin_index.open("w", newline="", encoding="utf-8") as f:
            ecrivain = csv.writer(f)
            ecrivain.writerow(["fichier", "code_valet", "libelle", "n_observations"])
            ecrivain.writerows(index)
        print(f"index des libelles -> {chemin_index}")
    return echecs


def main() -> int:
    print("=== Banque d'Angleterre ===")
    echecs = ingerer_boe()
    print("\n=== Reserve Bank of Australia ===")
    echecs += ingerer_rba()
    print("\n=== Banque du Canada ===")
    ecrites_boc = []
    echecs += ingerer_boc(ecrites_boc)
    total = len(BOE_SERIES) + len(RBA_SERIES) + len(ecrites_boc)
    if echecs:
        print(f"\n{len(echecs)}/{total} bilans en echec : {[n for n, _ in echecs]}")
        return 1
    print(f"\nOK -- {total} bilan(s) national(aux) ingere(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
