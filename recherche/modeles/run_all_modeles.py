"""Orchestrateur -- appelle main() de chaque modele en sequence, un modele casse n'interrompt
jamais les autres (meme discipline que global-macro-desk-cloud).

Usage :
    python run_all_modeles.py
"""

import importlib
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent

MODELES = [
    ("macro", "modele_regime_monetaire_emploi"),
    ("positionnement-comportemental", "modele_positionnement_cot"),
    ("statistique", "modele_correlations_positionnement"),
    ("series-temporelles", "modele_volatilite_ewma"),
    ("factorielle", "modele_momentum_prix"),
]


def main() -> int:
    echecs = []
    for lane, nom in MODELES:
        print(f"\n--- {lane}/{nom} ---")
        sys.path.insert(0, str(ICI / lane))
        try:
            module = importlib.import_module(nom)
            code = module.main()
            if code != 0:
                echecs.append(f"{lane}/{nom}")
        except Exception as e:
            print(f"{lane}/{nom} : exception non geree -- {e}")
            echecs.append(f"{lane}/{nom}")
        finally:
            sys.path.remove(str(ICI / lane))

    print(f"\n=== Resume : {len(MODELES) - len(echecs)}/{len(MODELES)} modeles OK ===")
    if echecs:
        print(f"En echec : {echecs}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
