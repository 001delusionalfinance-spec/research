"""Ingestion -- calendrier des reunions FOMC, passees et a venir (federalreserve.gov, source
officielle, aucune cle requise).

Cree le 2026-09-17 pour `modele_chemin_taux_fed.py` : ce modele a besoin de savoir
QUAND tombent les prochaines reunions pour situer ses lectures de taux implicites dans le
temps, ce qu'aucune ingestion existante ne fournissait -- `ingestion_fomc_statements.py` ne
liste que les 2 derniers communiques DEJA publies, jamais le calendrier a venir.

Meme page que `ingestion_fomc_statements.py` (`fomccalendars.htm`), lue differemment. Chaque
annee y est annoncee par un marqueur "<AAAA> FOMC Meetings" suivi de la liste des reunions au
format "<Mois> <JJ>-<JJ>" (ex: "September 15-16"), un "*" final marquant les reunions avec
Summary of Economic Projections (SEP, "dot plot").

Verifie en direct le 2026-09-17 : aucune reunion a cheval sur deux mois dans les annees
actuellement publiees sur la page (2026-2029). Si une apparaissait un jour ("April 30-May 1"),
le motif ci-dessous ne la capturerait pas -- elle disparaitrait silencieusement de cette
annee-la plutot que de lever une erreur. Garde-fou retenu : un compte total de reunions trop
bas (`< 8`, tous marqueurs annee confondus) fait echouer explicitement plutot que de laisser
passer un calendrier tronque sans le signaler.

Usage :
    python ingestion_fomc_calendrier.py
"""

import csv
import re
import sys
from pathlib import Path

import requests

CALENDAR_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
OUT_PATH = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "fomc" / "calendrier.csv"

MOIS = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
}
MOTIF_ANNEE = re.compile(r"(\d{4}) FOMC Meetings")
MOTIF_REUNION = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)"
    r" (\d{1,2})-(\d{1,2})(\*)?"
)
MIN_REUNIONS = 8  # repere : une seule annee complete en compte deja ~8 -- sert seulement a
                   # detecter un parsing casse (chute vers 0), pas une borne annee par annee.


def get_utf8(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    resp.raise_for_status()
    resp.encoding = "utf-8"  # meme prudence que ingestion_fomc_statements.py -- la page ne
                              # declare pas toujours son charset explicitement.
    return resp.text


def extraire_reunions(html: str) -> list:
    texte = re.sub(r"<[^>]+>", " ", html)
    texte = re.sub(r"\s+", " ", texte)

    marqueurs = list(MOTIF_ANNEE.finditer(texte))
    if not marqueurs:
        raise ValueError("aucun marqueur '<annee> FOMC Meetings' trouve -- page inattendue")

    reunions = []
    for i, m in enumerate(marqueurs):
        annee = int(m.group(1))
        debut_bloc = m.end()
        fin_bloc = marqueurs[i + 1].start() if i + 1 < len(marqueurs) else len(texte)
        bloc = texte[debut_bloc:fin_bloc]
        for rm in MOTIF_REUNION.finditer(bloc):
            mois_nom, jour_debut, jour_fin, projection = rm.groups()
            mois = MOIS[mois_nom]
            date_debut = f"{annee}-{mois:02d}-{int(jour_debut):02d}"
            date_fin = f"{annee}-{mois:02d}-{int(jour_fin):02d}"
            reunions.append((date_debut, date_fin, bool(projection)))
    return reunions


def main() -> int:
    try:
        html = get_utf8(CALENDAR_URL)
        reunions = extraire_reunions(html)
    except (requests.RequestException, ValueError) as e:
        print(f"echec -- {e}")
        return 1

    if len(reunions) < MIN_REUNIONS:
        print(f"echec -- seulement {len(reunions)} reunion(s) extraite(s) au total, "
              f"structure de page probablement changee")
        return 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    contenu = "date_debut,date_fin,projection_sep\n" + "".join(
        f"{d1},{d2},{proj}\n" for d1, d2, proj in sorted(set(reunions)))

    if OUT_PATH.exists() and OUT_PATH.read_text(encoding="utf-8") == contenu:
        print(f"OK -- calendrier inchange ({len(reunions)} reunions), fichier non reecrit")
        return 0

    OUT_PATH.write_text(contenu, encoding="utf-8")
    print(f"OK -- {len(reunions)} reunions FOMC (passees et a venir) -> {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
