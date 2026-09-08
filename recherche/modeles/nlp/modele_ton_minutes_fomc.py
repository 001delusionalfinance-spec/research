"""Modele -- diff de ton entre les 2 dernieres minutes FOMC (pas le communique -- un document
beaucoup plus riche, ~4500 mots vs ~150).

Meme lexique et meme methode que ton_fomc.py (coherence entre les deux modeles NLP FOMC), mais
sur un texte ~30x plus long -- le score de ton a plus de matiere pour se stabiliser, moins
sensible a un seul mot qui change. Complementaire, pas redondant : le communique est ce que le
comite VEUT dire publiquement en 150 mots choisis un par un, les minutes sont la discussion
INTERNE relativement moins polie (desaccords exprimes, doutes soulignes).
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "ton_minutes_fomc"
MINUTES_DIR = BRUT / "fomc_minutes"

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
    mots = re.findall(r"[a-z]+", texte.lower())
    if not mots:
        raise SerieVide("aucun mot exploitable")
    n_pos = sum(1 for m in mots if m in MOTS_POSITIFS)
    n_neg = sum(1 for m in mots if m in MOTS_NEGATIFS)
    score = (n_pos - n_neg) / len(mots) * 1000
    return score, len(mots), n_pos, n_neg


def main() -> int:
    fichiers = sorted(MINUTES_DIR.glob("*.txt")) if MINUTES_DIR.exists() else []
    if len(fichiers) < 2:
        print(f"echec -- moins de 2 fichiers dans {MINUTES_DIR}")
        return 1

    precedent, dernier = fichiers[-2], fichiers[-1]
    try:
        score_prec, n_mots_prec, pos_prec, neg_prec = score_ton(precedent.read_text(encoding="utf-8"))
        score_der, n_mots_der, pos_der, neg_der = score_ton(dernier.read_text(encoding="utf-8"))
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    diff_score = score_der - score_prec
    date_dernier = dernier.stem
    date_precedent = precedent.stem

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "date_precedente", "n_mots", "n_mots_positifs", "n_mots_negatifs",
         "score_ton_pour_mille", "diff_score_pour_mille"],
        [[date_dernier, date_precedent, n_mots_der, pos_der, neg_der, round(score_der, 3),
          round(diff_score, 3)]],
    )

    print(f"OK -- {date_precedent} -> {date_dernier} : ton {score_prec:+.2f}pm -> "
          f"{score_der:+.2f}pm (diff {diff_score:+.2f}pm), {n_mots_der} mots "
          f"({pos_der} positifs, {neg_der} negatifs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
