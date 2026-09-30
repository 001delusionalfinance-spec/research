"""Modele -- diff de ton entre les 2 derniers communiques FOMC + changement de vote/taux.

Consomme donnees/brut/fomc/ (ingestion_fomc_statements.py). Lexique de ton construit a la
main (~30 mots, PAS le Loughran-McDonald academique -- choix assume : un lexique generaliste financier serait mal calibre pour le
registre specifique des communiques de banque centrale). Score en pour-mille (mots de ton /
total mots x 1000), pas en pourcentage -- la difference entre deux communiques tient
generalement a 1-2 mots changes sur ~180, un pourcentage arrondirait a 0,0%.
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "ton_fomc"
# BRUT (via _lib.REPO_ROOT) plutot qu'un nouveau calcul de parents[N] a la main -- bug reel deja
# trouve deux fois dans ce depot (ingestion_fred.py, ingestion_cftc.py) en comptant les parents
# a la main pour un fichier a une profondeur differente ; BRUT est deja juste, ne pas le refaire.
FOMC_DIR = BRUT / "fomc"

# Lexique construit a la main pour le registre des communiques FOMC -- pas exhaustif,
# pas academique, un point de depart assume comme tel.
MOTS_POSITIFS = {
    "solid", "strong", "robust", "expanding", "resilient", "improving", "improved",
    "strengthened", "healthy", "stable", "gains", "growth",
}
MOTS_NEGATIFS = {
    "elevated", "uncertainty", "uncertain", "risks", "risk", "softening", "weakening",
    "weak", "slowing", "slowdown", "deteriorating", "deteriorated", "restrictive",
    "fragile", "concern", "concerns", "declined", "declining",
}


def score_ton(texte: str) -> tuple:
    """Retourne (score_pour_mille, nb_mots_total)."""
    mots = re.findall(r"[a-z]+", texte.lower())
    if not mots:
        raise SerieVide("aucun mot exploitable dans le texte")
    n_pos = sum(1 for m in mots if m in MOTS_POSITIFS)
    n_neg = sum(1 for m in mots if m in MOTS_NEGATIFS)
    score = (n_pos - n_neg) / len(mots) * 1000
    return score, len(mots)


def lire_votes() -> list:
    chemin = FOMC_DIR / "votes.csv"
    if not chemin.exists():
        raise SerieVide(f"{chemin} n'existe pas")
    with chemin.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if len(lignes) < 2:
        raise SerieVide("moins de 2 communiques ingeres -- diff impossible")
    return lignes


def main() -> int:
    try:
        votes = lire_votes()
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    precedent, dernier = votes[-2], votes[-1]

    try:
        texte_precedent = (FOMC_DIR / f"{precedent['date']}.txt").read_text(encoding="utf-8")
        texte_dernier = (FOMC_DIR / f"{dernier['date']}.txt").read_text(encoding="utf-8")
        score_prec, n_mots_prec = score_ton(texte_precedent)
        score_der, n_mots_der = score_ton(texte_dernier)
    except (FileNotFoundError, SerieVide) as e:
        print(f"echec -- {e}")
        return 1

    diff_score = score_der - score_prec
    taux_change = precedent["taux_cible"] != dernier["taux_cible"]
    dissidents_prec = len(precedent["dissidents"].split(";")) if precedent["dissidents"] else 0
    dissidents_der = len(dernier["dissidents"].split(";")) if dernier["dissidents"] else 0

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "date_precedente", "score_ton_pour_mille", "diff_score_pour_mille",
         "taux_cible", "taux_a_change", "dissidents", "nb_dissidents",
         "nb_dissidents_precedent"],
        [[dernier["date"], precedent["date"], round(score_der, 3), round(diff_score, 3),
          dernier["taux_cible"], taux_change, dernier["dissidents"], dissidents_der,
          dissidents_prec]],
    )

    if diff_score > 0.5:
        lecture = "ton qui s'ameliore"
    elif diff_score < -0.5:
        lecture = "ton qui se degrade"
    else:
        lecture = "ton stable"

    print(f"OK -- {precedent['date']} -> {dernier['date']} : "
          f"ton {score_prec:+.2f}‰ -> {score_der:+.2f}‰ (diff {diff_score:+.2f}‰, {lecture}), "
          f"taux {'change' if taux_change else 'inchange'} ({dernier['taux_cible']}), "
          f"dissidents {dissidents_prec} -> {dissidents_der}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
