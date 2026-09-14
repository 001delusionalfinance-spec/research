"""Ingestion Eurostat -- activite reelle et enquetes de conjoncture, zone euro et pays membres.

Comble l'absence totale de mesures d'activite hors US : production industrielle, ventes de
detail, chomage et enquete de confiance industrielle. Cote US, l'equivalent existe deja dans
`ingestion_fred.py` depuis le 2026-09-14.

**Correction d'un diagnostic errone du meme jour, a lire avant de conclure quoi que ce soit
sur Eurostat.** Une premiere exploration avait conclu "Eurostat est en retard, derniere
observation 2025-12" et la source avait ete ecartee. C'etait faux : ce retard est propre au
jeu **HICP** (`prc_hicp_manr`), pas a Eurostat en general. Les jeux d'activite ci-dessous sont
frais a 2026-07/2026-08. Le CPI reste ingere depuis le BIS (`ingestion_bis_cpi.py`), qui lui
est a jour -- inutile d'y revenir.

**Substitut du PMI.** Les PMI (S&P Global) et l'ISM sont proprietaires : aucune voie gratuite.
L'enquete de confiance industrielle de la Commission europeenne (`BS-ICI`) mesure la meme
chose -- un solde d'opinion d'entreprises sur leur activite -- est publique, mensuelle, et
couvre chaque pays membre. C'est le pendant europeen des enquetes Empire State / Philly Fed
retenues cote US, pas un pis-aller dissimule.

**Codes de dimension : chaque jeu a les siens, verifies un par un le 2026-09-14** (quatre
tentatives infructueuses avant d'y arriver -- les codes ne se devinent pas) :
- l'agregat zone euro est **`EA21`**, pas `EA20` : ce dernier existe comme code dans certains
  jeux mais n'y porte aucune valeur ;
- production industrielle : `indic_bt=PRD` et **pas** `PROD` ;
- ventes de detail : `indic_bt=VOL_SLS` et **pas** `TOVV`.

Structure JSON-stat : toutes les dimensions autres que le temps etant filtrees a une seule
valeur, la position aplatie dans `value` correspond directement a l'index temporel.

Usage :
    python ingestion_eurostat.py
"""

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BRUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "eurostat"
BASE = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{jeu}"
        "?format=JSON&lang=EN&{filtres}&geo={geo}")

# (nom de sortie, jeu, filtres hors geo, libelle, retard max en jours)
#
# Le retard tolere est propre a CHAQUE indicateur, pas global. Quatrieme fois de la journee
# que ce piege se presente (CPI trimestriel Australie/NZ, taux directeur Coree, service de la
# dette BIS, puis ici) : un seuil unique produit systematiquement des faux positifs. Cas
# present : la production industrielle de la ZONE EURO est parue a 2026-06 quand les pays
# membres etaient a 2026-07 -- normal, l'agregat attend la remontee de tous les membres.
# Un seuil commun a 100 jours la rejetait a 105 comme "gelee".
# Chaque entree porte AUSSI sa geographie : le code de la zone euro n'est pas le meme d'un jeu
# a l'autre (EA21 pour l'activite, EA20 pour le budgetaire). Verifie le 2026-09-14 -- utiliser
# le mauvais code renvoie une reponse structurellement valide mais VIDE, donc silencieuse.
PAYS = {"DE": "Allemagne", "FR": "France", "IT": "Italie", "ES": "Espagne"}
GEOS_ACTIVITE = {"EA21": "Zone euro", **PAYS}
GEOS_BUDGET = {"EA20": "Zone euro", **PAYS}

INDICATEURS = [
    ("production_industrielle", "sts_inpr_m",
     "indic_bt=PRD&s_adj=SCA&nace_r2=B-D&unit=I21", "Production industrielle", 130,
     GEOS_ACTIVITE),
    ("ventes_detail", "sts_trtu_m",
     "indic_bt=VOL_SLS&s_adj=SCA&nace_r2=G47&unit=I21", "Ventes de detail", 100,
     GEOS_ACTIVITE),
    ("chomage", "une_rt_m",
     "s_adj=SA&age=TOTAL&sex=T&unit=PC_ACT", "Taux de chomage", 100, GEOS_ACTIVITE),
    ("confiance_industrielle", "ei_bsin_m_r2",
     "indic=BS-ICI&s_adj=SA", "Confiance industrielle (substitut PMI)", 100, GEOS_ACTIVITE),
    # Budgetaire, ajoute le 2026-09-14 : le poste n'existait que pour les US. Trimestriel, donc
    # un seuil de peremption bien plus large (2026-Q1 au 2026-09-14, publication normale).
    ("dette_publique", "gov_10q_ggdebt",
     "sector=S13&na_item=GD&unit=PC_GDP", "Dette publique (% du PIB)", 300, GEOS_BUDGET),
    ("solde_public", "gov_10q_ggnfa",
     "sector=S13&na_item=B9&unit=PC_GDP", "Solde public (% du PIB)", 300, GEOS_BUDGET),
]

MIN_LIGNES = 24
TENTATIVES = 3


def fetch(jeu: str, filtres: str, geo: str) -> list:
    url = BASE.format(jeu=jeu, filtres=filtres, geo=geo)
    for essai in range(TENTATIVES):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "research/1.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=90) as resp:
                charge = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            if e.code < 500 or essai == TENTATIVES - 1:
                raise
            time.sleep(2 * (essai + 1))
        except (urllib.error.URLError, TimeoutError):
            if essai == TENTATIVES - 1:
                raise
            time.sleep(2 * (essai + 1))

    valeurs = charge.get("value") or {}
    if not valeurs:
        raise ValueError("aucune valeur renvoyee -- combinaison de filtres sans donnee")
    index_temps = charge["dimension"]["time"]["category"]["index"]
    periode_par_position = {position: periode for periode, position in index_temps.items()}

    points = []
    for cle, valeur in valeurs.items():
        periode = periode_par_position.get(int(cle))
        if periode is None or valeur is None:
            continue
        points.append((periode, float(valeur)))
    points.sort(key=lambda p: p[0])
    return points


def valider(points: list, nom: str, retard_max: int) -> None:
    if len(points) < MIN_LIGNES:
        raise ValueError(f"seulement {len(points)} ligne(s) pour {nom} -- snapshot degrade")
    brut = points[-1][0]
    if "-Q" in brut:   # les jeux budgetaires sont trimestriels ("2026-Q1")
        annee, trimestre = brut.split("-Q")
        derniere = datetime(int(annee), (int(trimestre) - 1) * 3 + 1, 1,
                            tzinfo=timezone.utc).date()
    else:
        annee, mois = brut.split("-")
        derniere = datetime(int(annee), int(mois), 1, tzinfo=timezone.utc).date()
    retard = (datetime.now(timezone.utc).date() - derniere).days
    if retard > retard_max:
        raise ValueError(f"derniere observation {points[-1][0]} pour {nom} -- {retard} jours "
                         f"de retard (seuil {retard_max}) : serie probablement gelee")
    # Aucun controle de signe : un solde d'opinion est negatif la plupart du temps.


def main() -> int:
    echecs = []
    total = 0
    for nom_ind, jeu, filtres, libelle, retard_max, geos in INDICATEURS:
        print(f"\n=== {libelle} ===")
        for geo, pays in geos.items():
            total += 1
            etiquette = f"{libelle} {pays}"
            try:
                points = fetch(jeu, filtres, geo)
                valider(points, etiquette, retard_max)
            except (ValueError, KeyError, urllib.error.URLError,
                    urllib.error.HTTPError, TimeoutError) as e:
                echecs.append((etiquette, str(e)))
                print(f"{pays} : echec -- {e}")
                time.sleep(0.6)
                continue

            dossier = BRUT_DIR / nom_ind
            dossier.mkdir(parents=True, exist_ok=True)
            chemin = dossier / f"{geo}.csv"
            with chemin.open("w", encoding="utf-8") as f:
                f.write("date,valeur\n")
                for periode, valeur in points:
                    f.write(f"{periode},{valeur:.6f}\n")
            print(f"{pays} : {len(points)} observations (jusqu'a {points[-1][0]}) -> {chemin}")
            time.sleep(0.6)

    if echecs:
        print(f"\n{len(echecs)}/{total} series en echec : {[n for n, _ in echecs]}")
        return 1
    print(f"\nOK -- {total} series Eurostat ingerees")
    return 0


if __name__ == "__main__":
    sys.exit(main())
