"""Modele -- frequence de mots-cles specifiques dans le communique FOMC le plus recent, suivie
dans le temps.

Complementaire de ton_fomc.py (score agrege positif/negatif) : suit des mots individuels
precis, choisis parce qu'ils ont un historique documente de signaler un virage de politique
("transitory" en 2021, "patient" en 2019 -- la presence/absence d'un mot specifique a parfois
plus de portee que le score de ton global). Compte brut, pas normalise par la longueur du texte
(volontaire : l'ABSENCE totale d'un mot est en soi une information, un ratio l'estomperait).
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "frequence_mots_cles_fomc"
FOMC_DIR = BRUT / "fomc"

MOTS_SUIVIS = [
    "uncertainty", "uncertain", "risks", "gradual", "patient", "transitory",
    "elevated", "solid", "strong", "resilient", "restrictive", "data-dependent",
]


def main() -> int:
    votes_csv = FOMC_DIR / "votes.csv"
    if not votes_csv.exists():
        print(f"echec -- {votes_csv} n'existe pas")
        return 1

    import csv
    with votes_csv.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        print("echec -- votes.csv vide")
        return 1

    date_communique = lignes[-1]["date"]
    chemin_texte = FOMC_DIR / f"{date_communique}.txt"
    if not chemin_texte.exists():
        print(f"echec -- {chemin_texte} n'existe pas")
        return 1

    texte = chemin_texte.read_text(encoding="utf-8").lower()
    mots = re.findall(r"[a-z\-]+", texte)
    total_mots = len(mots)
    if total_mots == 0:
        print("echec -- texte vide apres extraction")
        return 1

    comptes = {}
    for mot_cle in MOTS_SUIVIS:
        if "-" in mot_cle:
            comptes[mot_cle] = texte.count(mot_cle)
        else:
            comptes[mot_cle] = sum(1 for m in mots if m == mot_cle)

    presents = {m: c for m, c in comptes.items() if c > 0}
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "total_mots"] + MOTS_SUIVIS,
        [[date_communique, total_mots] + [comptes[m] for m in MOTS_SUIVIS]],
    )

    print(f"OK -- communique {date_communique}, {total_mots} mots -- mots-cles presents : "
          f"{presents if presents else 'aucun des mots suivis'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
