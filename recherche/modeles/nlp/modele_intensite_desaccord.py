"""Modele -- intensite du desaccord interne : combine le nombre de dissidents (deja extrait du
communique, ingestion_fomc_statements.py) avec la frequence de vocabulaire de desaccord dans
les minutes ("disagreed", "preferred", "dissent", "alternative view") -- un desaccord peut
exister sans dissidence formelle au vote (des membres peuvent exprimer un avis different sans
voter contre), ce texte le capture, pas seulement le decompte de voix.
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "intensite_desaccord"
MINUTES_DIR = BRUT / "fomc_minutes"
STATEMENTS_DIR = BRUT / "fomc"

MOTS_DESACCORD = ["disagreed", "preferred", "dissent", "alternative view", "some participants",
                   "a few participants", "several participants noted"]


def main() -> int:
    fichiers_minutes = sorted(MINUTES_DIR.glob("*.txt")) if MINUTES_DIR.exists() else []
    if not fichiers_minutes:
        print(f"echec -- aucun fichier dans {MINUTES_DIR}")
        return 1

    dernier = fichiers_minutes[-1]
    texte = dernier.read_text(encoding="utf-8").lower()
    date_minutes = dernier.stem

    comptes = {mot: texte.count(mot) for mot in MOTS_DESACCORD}
    total_mentions = sum(comptes.values())

    n_dissidents = 0
    votes_csv = STATEMENTS_DIR / "votes.csv"
    if votes_csv.exists():
        with votes_csv.open(encoding="utf-8") as f:
            lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
        correspondant = [l for l in lignes if l["date"] == date_minutes]
        if correspondant and correspondant[0]["dissidents"]:
            n_dissidents = len(correspondant[0]["dissidents"].split(";"))

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_dissidents_vote", "n_mentions_desaccord_texte", "total_mentions"],
        [[date_minutes, n_dissidents, str(comptes), total_mentions]],
    )

    print(f"OK -- minutes {date_minutes} : {n_dissidents} dissident(s) au vote, "
          f"{total_mentions} mention(s) de desaccord dans le texte ({comptes})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
