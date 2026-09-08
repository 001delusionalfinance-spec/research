"""Modele -- indice de langage prudent/qualificatif ("hedging language") dans les minutes --
frequence de mots qui nuancent une affirmation plutot que de l'exprimer avec certitude
("however", "but", "likely", "somewhat", "may", "could", "appeared").

Distinct du score de ton (positif/negatif) et des mots-cles thematiques deja suivis : ici, le
DEGRE DE CERTITUDE du langage, independant de sa charge. Un comite qui qualifie beaucoup ses
affirmations peut signaler une incertitude de jugement, meme avec un ton par ailleurs neutre ou
positif.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "langage_prudence"
MINUTES_DIR = BRUT / "fomc_minutes"

MOTS_PRUDENCE = {
    "however", "but", "likely", "somewhat", "may", "might", "could", "appeared",
    "seemed", "roughly", "broadly", "generally", "relatively", "largely",
}


def main() -> int:
    fichiers = sorted(MINUTES_DIR.glob("*.txt")) if MINUTES_DIR.exists() else []
    if not fichiers:
        print(f"echec -- aucun fichier dans {MINUTES_DIR}")
        return 1

    dernier = fichiers[-1]
    texte = dernier.read_text(encoding="utf-8").lower()
    mots = re.findall(r"[a-z]+", texte)
    total_mots = len(mots)
    if total_mots == 0:
        print("echec -- texte vide")
        return 1

    n_prudence = sum(1 for m in mots if m in MOTS_PRUDENCE)
    indice_pour_mille = n_prudence / total_mots * 1000
    date_minutes = dernier.stem

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_mots_prudence", "total_mots", "indice_pour_mille"],
        [[date_minutes, n_prudence, total_mots, round(indice_pour_mille, 3)]],
    )

    if indice_pour_mille > 15:
        lecture = "langage prudent"
    elif indice_pour_mille < 8:
        lecture = "langage direct"
    else:
        lecture = "langage moderement prudent"

    print(f"OK -- minutes {date_minutes} : {n_prudence} mots de prudence sur {total_mots} "
          f"({indice_pour_mille:.2f} pour mille, {lecture})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
