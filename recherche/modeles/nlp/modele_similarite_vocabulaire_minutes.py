"""Modele -- similarite de vocabulaire (indice de Jaccard) entre les 2 dernieres minutes FOMC.

Distinct du score de ton (positif/negatif) : ici, combien le VOCABULAIRE UTILISE change d'une
reunion a l'autre, independamment de sa charge positive/negative -- un comite qui reformule
largement son discours (indice bas) signale un changement de cadre de lecture plus profond
qu'un simple ajustement de ton sur un vocabulaire stable (indice haut). Jaccard = |mots
communs| / |union des mots|, sur les mots uniques (pas le compte d'occurrences) de chaque texte.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "similarite_vocabulaire_minutes"
MINUTES_DIR = BRUT / "fomc_minutes"

MOTS_VIDES = {
    "the", "a", "an", "of", "to", "in", "and", "for", "on", "that", "with", "as", "by",
    "was", "were", "is", "are", "be", "been", "this", "it", "at", "from", "would", "will",
    "their", "its", "had", "have", "has", "not", "or", "which", "also", "these", "than",
}


def mots_uniques(texte: str) -> set:
    mots = re.findall(r"[a-z]+", texte.lower())
    return {m for m in mots if m not in MOTS_VIDES and len(m) > 2}


def main() -> int:
    fichiers = sorted(MINUTES_DIR.glob("*.txt")) if MINUTES_DIR.exists() else []
    if len(fichiers) < 2:
        print(f"echec -- moins de 2 fichiers dans {MINUTES_DIR}")
        return 1

    precedent, dernier = fichiers[-2], fichiers[-1]
    mots_prec = mots_uniques(precedent.read_text(encoding="utf-8"))
    mots_der = mots_uniques(dernier.read_text(encoding="utf-8"))

    if not mots_prec or not mots_der:
        print("echec -- vocabulaire vide sur au moins un des deux textes")
        return 1

    intersection = mots_prec & mots_der
    union = mots_prec | mots_der
    jaccard = len(intersection) / len(union)

    mots_nouveaux = mots_der - mots_prec
    mots_disparus = mots_prec - mots_der

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "date_precedente", "n_mots_uniques_dernier", "n_mots_uniques_precedent",
         "jaccard", "n_mots_nouveaux", "n_mots_disparus"],
        [[dernier.stem, precedent.stem, len(mots_der), len(mots_prec), round(jaccard, 4),
          len(mots_nouveaux), len(mots_disparus)]],
    )

    print(f"OK -- {precedent.stem} -> {dernier.stem} : Jaccard={jaccard:.4f} "
          f"({len(intersection)} mots communs / {len(union)} mots uniques au total), "
          f"{len(mots_nouveaux)} nouveaux, {len(mots_disparus)} disparus")
    return 0


if __name__ == "__main__":
    sys.exit(main())
