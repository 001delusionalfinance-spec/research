"""Ingestion BIS -- indices de prix a la consommation, multi-pays.

Comble le trou le plus genant du repo : **l'inflation hors US**, absente jusqu'au 2026-09-14.

Pourquoi le BIS et pas les sources tentees avant -- chacune testee en direct le 2026-09-14,
resultat mesure et pas suppose :

| Source tentee                | Derniere observation | Verdict                          |
|------------------------------|----------------------|----------------------------------|
| FRED (series OCDE)           | 2021-06 a 2025-04    | gelees, deja rejetees le 08/09   |
| Eurostat `prc_hicp_manr`     | 2025-12              | trop en retard                   |
| BCE Data Portal (ICP)        | 2025-12              | identique a Eurostat (meme source)|
| DBnomics / OCDE `DP_LIVE`    | 2023-11              | jeu deprecie                     |
| DBnomics / FMI `CPI`         | 2025-07              | ~14 mois de retard                |
| ONS UK (API timeseries)      | HTTP 404             | chemin invalide                  |
| **BIS `WS_LONG_CPI`**        | **2026-06 / 2026-07**| **retenu**                       |

Detail technique qui a coute du temps : l'API BIS renvoie **HTTP 406** avec un `Accept`
generique. Il faut exactement `application/vnd.sdmx.data+json;version=1.0.0`. Et la charge
utile SDMX-JSON place `structure` et `dataSets` **sous la cle `data`**, pas a la racine
comme d'autres implementations SDMX -- d'ou le parseur ci-dessous.

Ce qui est ingere : l'**indice** de prix brut, jamais un taux de variation. Conforme a la
regle du repo (`donnees/brut/` = non transforme) : calculer l'inflation en glissement annuel
est le travail d'un modele, pas de l'ingestion.

Couverture : 11 blocs verifies frais + les US. Les US restent par ailleurs couverts par
`CPIAUCSL` dans `ingestion_fred.py` (mensuel, ~1 mois de retard) -- la serie BIS est ingeree
en plus pour que les comparaisons entre blocs reposent sur une source homogene, pas pour la
remplacer.

Usage :
    python ingestion_bis_cpi.py
"""

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BRUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "bis" / "cpi"
BIS_URL = ("https://stats.bis.org/api/v2/data/dataflow/BIS/WS_LONG_CPI/1.0/M.{code}.628")
ACCEPT_SDMX = "application/vnd.sdmx.data+json;version=1.0.0"

PAYS = {
    "XM": "Zone euro",
    "GB": "Royaume-Uni",
    "JP": "Japon",
    "CN": "Chine",
    "KR": "Coree",
    "CA": "Canada",
    "AU": "Australie",
    "CH": "Suisse",
    "SE": "Suede",
    "NO": "Norvege",
    "NZ": "Nouvelle-Zelande",
    "US": "Etats-Unis",
}

MIN_LIGNES = 24

# Le seuil de peremption depend de la FREQUENCE DE PUBLICATION du pays, pas d'une valeur
# unique. Erreur reelle commise au premier test du 2026-09-14 : un seuil global de 100 jours
# rejetait l'Australie et la Nouvelle-Zelande a 105 jours comme "probablement gelees", alors
# que leur CPI est **trimestriel** -- une observation de juin consultee mi-septembre est
# parfaitement a jour pour elles. Le garde-fou faisait son travail, c'est la regle qui
# ignorait la frequence.
#   - mensuel   : periode + 1 a 2 mois de publication -> 100 jours de marge
#   - trimestriel : periode + un trimestre + publication -> 160 jours de marge
RETARD_MAX_MENSUEL = 100
RETARD_MAX_TRIMESTRIEL = 160
PAYS_TRIMESTRIELS = {"AU", "NZ"}

TENTATIVES = 3


def fetch_cpi(code: str) -> list:
    """Renvoie [(periode 'AAAA-MM', valeur float)] triee par date croissante."""
    url = BIS_URL.format(code=code)
    derniere_erreur = None
    for essai in range(TENTATIVES):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "research/1.0", "Accept": ACCEPT_SDMX},
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                charge = json.loads(resp.read().decode("utf-8"))
            break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            # Timeouts transitoires observes au test (les US ont echoue une fois puis repondu).
            derniere_erreur = e
            if essai == TENTATIVES - 1:
                raise
            time.sleep(2 * (essai + 1))
    else:  # pragma: no cover -- la boucle sort par break ou par raise
        raise derniere_erreur

    data = charge.get("data")
    if not data:
        raise ValueError(f"reponse BIS sans bloc 'data' pour {code}")

    periodes = data["structure"]["dimensions"]["observation"][0]["values"]
    series = data["dataSets"][0].get("series") or {}
    if not series:
        raise ValueError(f"aucune serie renvoyee pour {code}")
    observations = list(series.values())[0]["observations"]

    points = []
    for index_str, valeurs in observations.items():
        brut = valeurs[0]
        if brut is None or brut == "":
            continue
        points.append((periodes[int(index_str)]["id"], float(brut)))
    points.sort(key=lambda p: p[0])
    return points


def valider(points: list, nom: str, code: str) -> None:
    if not points:
        raise ValueError(f"aucune donnee renvoyee pour {nom}")
    if len(points) < MIN_LIGNES:
        raise ValueError(f"seulement {len(points)} ligne(s) pour {nom} -- snapshot degrade")
    if any(v <= 0 for _, v in points):
        raise ValueError(f"indice de prix <= 0 pour {nom} -- donnee corrompue")

    annee, mois = points[-1][0].split("-")
    derniere = datetime(int(annee), int(mois), 1, tzinfo=timezone.utc).date()
    retard = (datetime.now(timezone.utc).date() - derniere).days
    seuil = (RETARD_MAX_TRIMESTRIEL if code in PAYS_TRIMESTRIELS else RETARD_MAX_MENSUEL)
    if retard > seuil:
        raise ValueError(f"derniere observation {points[-1][0]} pour {nom} -- {retard} jours "
                         f"de retard (seuil {seuil}) : serie probablement gelee")


def main() -> int:
    echecs = []
    for code, nom in PAYS.items():
        try:
            points = fetch_cpi(code)
            valider(points, nom, code)
        except (ValueError, urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
            continue

        BRUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = BRUT_DIR / f"{code}.csv"
        with out_path.open("w", encoding="utf-8") as f:
            f.write("date,indice\n")
            for periode, valeur in points:
                f.write(f"{periode},{valeur:.6f}\n")
        print(f"{nom} : {len(points)} observations (jusqu'a {points[-1][0]}) -> {out_path}")
        time.sleep(0.8)  # l'API BIS coupe sous rafale, constate au test du 2026-09-14

    if echecs:
        print(f"\n{len(echecs)}/{len(PAYS)} blocs en echec : {[n for n, _ in echecs]}")
        return 1

    print(f"\nOK -- {len(PAYS)} blocs de prix ingeres")
    return 0


if __name__ == "__main__":
    sys.exit(main())
