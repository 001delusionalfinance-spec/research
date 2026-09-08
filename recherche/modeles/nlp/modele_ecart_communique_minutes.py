"""Modele -- ecart de ton entre le communique (public, ~150 mots polis) et les minutes
(discussion interne, ~4500 mots) de la MEME reunion FOMC.

Hypothese testable : si le communique est beaucoup plus positif que les minutes de la meme
reunion, le message public "lisse" des tensions internes reelles -- un ecart qui se creuse dans
le temps serait un signal a surveiller (le marche lit le communique, pas les minutes, qui
sortent 3 semaines plus tard). Reutilise entierement les donnees deja ingerees par
ingestion_fomc_statements.py et ingestion_fomc_minutes.py, aucune nouvelle source.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "ecart_communique_minutes"
STATEMENTS_DIR = BRUT / "fomc"
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


def score_ton(texte: str) -> float:
    mots = re.findall(r"[a-z]+", texte.lower())
    if not mots:
        raise SerieVide("aucun mot exploitable")
    n_pos = sum(1 for m in mots if m in MOTS_POSITIFS)
    n_neg = sum(1 for m in mots if m in MOTS_NEGATIFS)
    return (n_pos - n_neg) / len(mots) * 1000


def main() -> int:
    fichiers_minutes = sorted(MINUTES_DIR.glob("*.txt")) if MINUTES_DIR.exists() else []
    if not fichiers_minutes:
        print(f"echec -- aucun fichier dans {MINUTES_DIR}")
        return 1

    derniere_minute = fichiers_minutes[-1]
    date_reunion = derniere_minute.stem
    chemin_communique = STATEMENTS_DIR / f"{date_reunion}.txt"
    if not chemin_communique.exists():
        print(f"echec -- {chemin_communique} n'existe pas (communique de la meme reunion "
              f"pas ingere)")
        return 1

    try:
        score_communique = score_ton(chemin_communique.read_text(encoding="utf-8"))
        score_minutes = score_ton(derniere_minute.read_text(encoding="utf-8"))
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    ecart = score_communique - score_minutes
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date_reunion", "score_ton_communique", "score_ton_minutes", "ecart_pour_mille"],
        [[date_reunion, round(score_communique, 3), round(score_minutes, 3),
          round(ecart, 3)]],
    )

    print(f"OK -- reunion {date_reunion} : communique={score_communique:+.2f}pm, "
          f"minutes={score_minutes:+.2f}pm -- ecart={ecart:+.2f}pm "
          f"({'communique plus positif' if ecart > 0 else 'minutes plus positives'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
