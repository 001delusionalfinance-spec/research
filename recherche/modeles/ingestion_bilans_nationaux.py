"""Ingestion des bilans de banques centrales absents de FRED.

`ingestion_fred.py` couvre les bilans de la Fed (avec ses composantes), de la BCE et de la
Banque du Japon. Ce fichier prend le relais pour les banques centrales que FRED n'expose pas,
en allant chez elles.

Etat de la recherche menee le 2026-09-14, gardee ici pour ne pas etre refaite a l'aveugle :

| Banque centrale | Resultat                                                              |
|-----------------|-----------------------------------------------------------------------|
| **Banque d'Angleterre** | **Retenue** -- serie `RPWB55A` de sa base statistique, hebdomadaire |
| Banque du Canada | Aucun groupe de bilan trouve sur l'API Valet (trois noms testes, tous en 404). Les series existent probablement sous un autre identifiant, non trouve |
| Riksbank | Aucune serie de bilan exposee par l'API SWEA (liste complete parcourue) |
| SNB, PBOC, RBA, RBNZ, Norges | Non explores a ce stade |

Pourquoi ca compte : une banque centrale peut laisser son taux directeur inchange et durcir
fortement en laissant son bilan se reduire. Sans les bilans, on ne lit qu'une moitie de la
politique monetaire -- et pour l'instant cette moitie n'est visible que pour la Fed, la BCE,
la Banque du Japon et desormais la Banque d'Angleterre.

Usage :
    python ingestion_bilans_nationaux.py
"""

import csv
import io
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


def main() -> int:
    print("=== Banque d'Angleterre ===")
    echecs = ingerer_boe()
    total = len(BOE_SERIES)
    if echecs:
        print(f"\n{len(echecs)}/{total} bilans en echec : {[n for n, _ in echecs]}")
        return 1
    print(f"\nOK -- {total} bilan(s) national(aux) ingere(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
