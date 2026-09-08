"""Modele -- longueur/complexite des minutes FOMC (memes metriques que
complexite_texte_fomc.py, appliquees aux minutes -- document ~30x plus long, la variation
d'une reunion a l'autre a plus de signal statistique sur un texte plus long).
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "complexite_texte_minutes"
MINUTES_DIR = BRUT / "fomc_minutes"


def main() -> int:
    fichiers = sorted(MINUTES_DIR.glob("*.txt")) if MINUTES_DIR.exists() else []
    if not fichiers:
        print(f"echec -- aucun fichier dans {MINUTES_DIR}")
        return 1

    dernier = fichiers[-1]
    texte = dernier.read_text(encoding="utf-8")
    phrases = [p.strip() for p in re.split(r"[.!?]", texte) if p.strip()]
    mots = re.findall(r"[A-Za-z]+", texte)

    if not phrases or not mots:
        print("echec -- texte vide ou non exploitable")
        return 1

    n_mots = len(mots)
    n_phrases = len(phrases)
    longueur_moyenne_phrase = n_mots / n_phrases
    mots_longs = [m for m in mots if len(m) > 6]
    part_mots_longs = len(mots_longs) / n_mots
    date_minutes = dernier.stem

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_mots", "n_phrases", "longueur_moyenne_phrase", "part_mots_longs_pct"],
        [[date_minutes, n_mots, n_phrases, round(longueur_moyenne_phrase, 2),
          round(part_mots_longs * 100, 2)]],
    )

    if longueur_moyenne_phrase > 20:
        lecture_phrase = "phrases longues"
    elif longueur_moyenne_phrase < 12:
        lecture_phrase = "phrases courtes"
    else:
        lecture_phrase = "phrases de longueur moderee"
    lecture_vocab = "vocabulaire dense" if part_mots_longs > 0.30 else "vocabulaire simple"

    print(f"OK -- minutes {date_minutes} : {n_mots} mots, {n_phrases} phrases "
          f"({longueur_moyenne_phrase:.1f} mots/phrase, {lecture_phrase}), {part_mots_longs * 100:.1f}% de mots "
          f"longs (>6 lettres, {lecture_vocab})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
