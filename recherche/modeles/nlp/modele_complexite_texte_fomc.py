"""Modele -- longueur et complexite du texte du communique FOMC le plus recent, comme proxy
d'incertitude redactionnelle du comite.

Hypothese testable, pas une certitude : un comite qui hesite/negocie un compromis peut produire
un texte plus long et plus alambique qu'un comite aligne sur un message simple. Longueur en
mots, longueur moyenne de phrase, part de mots longs (>6 lettres, proxy grossier de
jargon/complexite -- pas un vrai indice de lisibilite comme Flesch-Kincaid, volontairement plus
simple, a raffiner si utile).
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "complexite_texte_fomc"
FOMC_DIR = BRUT / "fomc"


def main() -> int:
    votes_csv = FOMC_DIR / "votes.csv"
    if not votes_csv.exists():
        print(f"echec -- {votes_csv} n'existe pas")
        return 1

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

    texte = chemin_texte.read_text(encoding="utf-8")
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

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_mots", "n_phrases", "longueur_moyenne_phrase", "part_mots_longs_pct"],
        [[date_communique, n_mots, n_phrases, round(longueur_moyenne_phrase, 2),
          round(part_mots_longs * 100, 2)]],
    )

    print(f"OK -- communique {date_communique} : {n_mots} mots, {n_phrases} phrases "
          f"({longueur_moyenne_phrase:.1f} mots/phrase en moyenne), "
          f"{part_mots_longs * 100:.1f}% de mots longs (>6 lettres)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
