"""Modele -- extraction d'entites geographiques/institutionnelles dans les minutes FOMC --
combien de fois chaque region/institution est mentionnee, proxy de "focus" du comite.

Liste construite a la main (pas de vrai NER/spaCy -- comptage de mots-cles, meme discipline
assumee que le lexique de ton dans ton_fomc.py : simple, pas academique, documente comme tel).
Complementaire du score de ton : SUR QUOI le comite se concentre, pas seulement avec quel ton.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "entites_geographiques_minutes"
MINUTES_DIR = BRUT / "fomc_minutes"

ENTITES = {
    "Middle East": ["middle east"],
    "China": ["china", "chinese"],
    "Europe": ["europe", "european", "euro area"],
    "Japan": ["japan", "japanese"],
    "Mexico": ["mexico", "mexican"],
    "Canada": ["canada", "canadian"],
    "labor_market": ["labor market", "employment"],
    "inflation": ["inflation"],
    "tariffs": ["tariff"],
    "housing": ["housing"],
}


def main() -> int:
    fichiers = sorted(MINUTES_DIR.glob("*.txt")) if MINUTES_DIR.exists() else []
    if not fichiers:
        print(f"echec -- aucun fichier dans {MINUTES_DIR}")
        return 1

    dernier = fichiers[-1]
    texte = dernier.read_text(encoding="utf-8").lower()
    date_minutes = dernier.stem

    comptes = {}
    for entite, mots_cles in ENTITES.items():
        comptes[entite] = sum(texte.count(mc) for mc in mots_cles)

    presents = {e: c for e, c in comptes.items() if c > 0}
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date"] + list(ENTITES.keys()),
        [[date_minutes] + [comptes[e] for e in ENTITES]],
    )

    print(f"OK -- minutes {date_minutes} -- mentions : {presents}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
