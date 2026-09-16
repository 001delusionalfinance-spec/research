"""Ingestion des courbes souveraines non-US en frequence QUOTIDIENNE.

Probleme resolu : `ingestion_fred.py` ne couvrait les souverains non-US qu'en **mensuel**
(series OCDE `IRLTLT01..`, un seul point de courbe, le 10 ans). Un differentiel de taux entre
deux pays calcule sur du mensuel ne sert a rien pour lire le FX, qui bouge tous les jours.
Chaque source ci-dessous est la source **officielle nationale**, verifiee en direct le
2026-09-14.

Trois sources, volontairement isolees les unes des autres : un echec sur l'une ne doit pas
empecher les deux autres d'aboutir.

- **Zone euro** -- API du portail de donnees de la BCE (SDMX-JSON). Deux courbes distinctes
  sont ingerees et ce n'est pas un doublon : `G_N_A` ne retient que les emetteurs notes AAA
  (la courbe "sans risque" de la zone), `G_N_C` retient tous les emetteurs (elle inclut donc
  la prime de risque souverain des pays peripheriques). L'ecart entre les deux est lui-meme
  une mesure de stress intra-zone.
  Attention : la charge SDMX de la BCE place `structure` a la RACINE, contrairement au BIS
  qui la place sous `data` (cf. `ingestion_bis_cpi.py`). Deux implementations SDMX
  differentes, deux parseurs differents.

- **Royaume-Uni** -- base statistique interactive de la Banque d'Angleterre (export CSV).

- **Japon** -- Ministere des Finances, fichier historique complet de la courbe JGB
  (~13 000 jours, toutes maturites de 1 a 40 ans). Le fichier de l'annee courante existe
  aussi mais n'apporte rien de plus : l'historique est deja a jour.

Usage :
    python ingestion_souverains_quotidiens.py
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

ECB_URL = "https://data-api.ecb.europa.eu/service/data/YC/{cle}?format=jsondata"
# Courbe elargie le 2026-09-14 : de 3 a 8 maturites AAA. Une courbe a trois points ne permet
# pas de lire une deformation (pentification par l'avant contre par l'arriere, bosse sur le
# ventre) -- il faut les points intermediaires.
ECB_SERIES = {
    "ZONE_EURO_AAA_1A": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_1Y",
    "ZONE_EURO_AAA_2A": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y",
    "ZONE_EURO_AAA_3A": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_3Y",
    "ZONE_EURO_AAA_5A": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_5Y",
    "ZONE_EURO_AAA_7A": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_7Y",
    "ZONE_EURO_AAA_10A": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y",
    "ZONE_EURO_AAA_20A": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_20Y",
    "ZONE_EURO_AAA_30A": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_30Y",
    "ZONE_EURO_TOUS_10A": "B.U2.EUR.4F.G_N_C.SV_C_YM.SR_10Y",
}

BOE_URL = ("https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp?csv.x=yes"
           "&Datefrom=01/Jan/1990&Dateto=now&SeriesCodes={code}&CSVF=TN&UsingCodes=Y"
           "&VPD=Y&VFD=N")
BOE_SERIES = {
    "UK_5A": "IUDSNPY",
    "UK_10A": "IUDMNZC",
    "UK_20A": "IUDLNPY",
}

MOF_URL = ("https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/"
           "jgbcme_all.csv")
# Colonnes du fichier MOF a retenir, par intitule exact de maturite dans l'entete.
MOF_MATURITES = {"2Y": "JAPON_2A", "5Y": "JAPON_5A", "10Y": "JAPON_10A", "30Y": "JAPON_30A"}

# Seuil de peremption par SOURCE, pas global -- chaque emetteur a son propre rythme de
# publication. Constate le 2026-09-14 : la BCE et la Banque d'Angleterre publient a J-4
# (2026-09-10), le MOF japonais met a jour son fichier historique par lots de fin de mois
# (derniere donnee 2026-08-31, soit 14 jours). Un seuil unique a 15 jours passait de justesse
# pour le Japon et aurait casse des le mois suivant.
RETARD_MAX_QUOTIDIEN = 15   # BCE, Banque d'Angleterre
RETARD_MAX_MOF = 45         # Japon, mise a jour mensuelle du fichier historique
MIN_LIGNES = 100


def _ecrire(nom: str, points: list) -> None:
    BRUT_DIR.mkdir(parents=True, exist_ok=True)
    chemin = BRUT_DIR / f"{nom}.csv"
    with chemin.open("w", encoding="utf-8") as f:
        f.write("date,taux\n")
        for date_str, valeur in points:
            f.write(f"{date_str},{valeur:.6f}\n")
    print(f"{nom} : {len(points)} lignes (jusqu'a {points[-1][0]}) -> {chemin}")


def _valider(points: list, nom: str, retard_max: int = RETARD_MAX_QUOTIDIEN) -> None:
    if len(points) < MIN_LIGNES:
        raise ValueError(f"seulement {len(points)} ligne(s) pour {nom} -- snapshot degrade")
    derniere = datetime.strptime(points[-1][0], "%Y-%m-%d").date()
    retard = (datetime.now(timezone.utc).date() - derniere).days
    if retard > retard_max:
        raise ValueError(f"derniere donnee du {points[-1][0]} pour {nom} -- {retard} jours de "
                         f"retard (seuil {retard_max})")
    # Aucun controle de signe : un taux souverain peut etre negatif (Japon et zone euro l'ont
    # ete pendant des annees). Un tel controle serait une erreur de modele, pas une securite.


def _http(url: str, accept: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": accept})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def ingerer_bce() -> list:
    echecs = []
    for nom, cle in ECB_SERIES.items():
        try:
            charge = json.loads(_http(ECB_URL.format(cle=cle), "application/json"))
            # Charge BCE : `structure` a la racine (contrairement au BIS, sous `data`).
            periodes = charge["structure"]["dimensions"]["observation"][0]["values"]
            observations = list(charge["dataSets"][0]["series"].values())[0]["observations"]
            points = sorted(
                (periodes[int(i)]["id"], float(v[0]))
                for i, v in observations.items() if v[0] is not None)
            _valider(points, nom)
            _ecrire(nom, points)
        except (ValueError, KeyError, IndexError, urllib.error.URLError,
                urllib.error.HTTPError, TimeoutError) as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
    return echecs


def ingerer_boe() -> list:
    echecs = []
    for nom, code in BOE_SERIES.items():
        try:
            texte = _http(BOE_URL.format(code=code), "text/csv")
            lignes = [r for r in csv.reader(io.StringIO(texte)) if r and len(r) >= 2]
            points = []
            for date_brute, valeur in ((r[0], r[1]) for r in lignes[1:]):
                if not valeur.strip():
                    continue
                # Format Banque d'Angleterre : "10 Sep 2026"
                jour = datetime.strptime(date_brute.strip(), "%d %b %Y").date()
                points.append((jour.isoformat(), float(valeur)))
            points.sort()
            _valider(points, nom)
            _ecrire(nom, points)
        except (ValueError, IndexError, urllib.error.URLError,
                urllib.error.HTTPError, TimeoutError) as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
    return echecs


def ingerer_mof() -> list:
    try:
        texte = _http(MOF_URL, "text/csv")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"JAPON : echec -- {e}")
        return [("JAPON", str(e))]

    lignes = [r for r in csv.reader(io.StringIO(texte)) if r]
    # La premiere ligne du fichier MOF est un TITRE ("Interest Rate ... (Unit : %)"), pas
    # l'entete. Les maturites sont sur la ligne suivante. On cherche la ligne dont la premiere
    # cellule vaut "Date" plutot que de coder en dur un indice, pour survivre a un decalage.
    index_entete = next((i for i, r in enumerate(lignes[:10])
                         if r and r[0].strip().lower() == "date"), None)
    if index_entete is None:
        print(f"JAPON : echec -- ligne d'entete 'Date' introuvable dans {lignes[0][:4]}")
        return [("JAPON", "entete introuvable")]
    entete = [c.strip() for c in lignes[index_entete]]
    colonnes = {}
    for etiquette, nom in MOF_MATURITES.items():
        if etiquette in entete:
            colonnes[entete.index(etiquette)] = nom
    if not colonnes:
        print(f"JAPON : echec -- aucune maturite attendue dans l'entete {entete[:8]}")
        return [("JAPON", "entete inattendue")]

    series = {nom: [] for nom in colonnes.values()}
    for ligne in lignes[index_entete + 1:]:
        if not ligne or not ligne[0].strip():
            continue
        try:
            jour = datetime.strptime(ligne[0].strip(), "%Y/%m/%d").date().isoformat()
        except ValueError:
            continue  # lignes d'entete repetees ou separateurs
        for index, nom in colonnes.items():
            if index >= len(ligne):
                continue
            brut = ligne[index].strip()
            if not brut or brut == "-":
                continue
            try:
                series[nom].append((jour, float(brut)))
            except ValueError:
                continue

    echecs = []
    for nom, points in series.items():
        try:
            points.sort()
            _valider(points, nom, RETARD_MAX_MOF)
            _ecrire(nom, points)
        except ValueError as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
    return echecs


def main() -> int:
    print("=== Zone euro (BCE) ===")
    echecs = ingerer_bce()
    print("\n=== Royaume-Uni (Banque d'Angleterre) ===")
    echecs += ingerer_boe()
    print("\n=== Japon (Ministere des Finances) ===")
    echecs += ingerer_mof()

    total = len(ECB_SERIES) + len(BOE_SERIES) + len(MOF_MATURITES)
    if echecs:
        print(f"\n{len(echecs)}/{total} courbes en echec : {[n for n, _ in echecs]}")
        return 1
    print(f"\nOK -- {total} courbes souveraines quotidiennes ingerees")
    return 0


if __name__ == "__main__":
    sys.exit(main())
