"""Modele -- frequence de mots-cles specifiques dans les minutes (meme lexique que
modele_frequence_mots_cles_fomc.py, applique aux minutes) -- parallele complet communique/
minutes pour cette dimension, comme deja fait pour le ton et la complexite.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "frequence_mots_cles_minutes"
MINUTES_DIR = BRUT / "fomc_minutes"

MOTS_SUIVIS = [
    "uncertainty", "uncertain", "risks", "gradual", "patient", "transitory",
    "elevated", "solid", "strong", "resilient", "restrictive", "data-dependent",
]


def main() -> int:
    fichiers = sorted(MINUTES_DIR.glob("*.txt")) if MINUTES_DIR.exists() else []
    if not fichiers:
        print(f"echec -- aucun fichier dans {MINUTES_DIR}")
        return 1

    dernier = fichiers[-1]
    texte = dernier.read_text(encoding="utf-8").lower()
    mots = re.findall(r"[a-z\-]+", texte)
    total_mots = len(mots)
    if total_mots == 0:
        print("echec -- texte vide")
        return 1

    comptes = {}
    for mot_cle in MOTS_SUIVIS:
        if "-" in mot_cle:
            comptes[mot_cle] = texte.count(mot_cle)
        else:
            comptes[mot_cle] = sum(1 for m in mots if m == mot_cle)

    date_minutes = dernier.stem
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "total_mots"] + MOTS_SUIVIS,
        [[date_minutes, total_mots] + [comptes[m] for m in MOTS_SUIVIS]],
    )

    presents = {m: c for m, c in comptes.items() if c > 0}
    print(f"OK -- minutes {date_minutes}, {total_mots} mots -- mots-cles : {presents}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
