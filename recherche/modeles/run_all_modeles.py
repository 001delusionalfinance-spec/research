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
    ("macro", "modele_sahm_rule"),
    ("macro", "modele_taux_reel_us"),
    ("positionnement-comportemental", "modele_positionnement_cot"),
    ("positionnement-comportemental", "modele_momentum_positionnement"),
    ("positionnement-comportemental", "modele_crowding_cross_asset"),
    ("statistique", "modele_correlations_positionnement"),
    ("statistique", "modele_stationnarite_taux"),
    ("statistique", "modele_correlation_glissante"),
    ("series-temporelles", "modele_volatilite_ewma"),
    ("series-temporelles", "modele_garch"),
    ("series-temporelles", "modele_hurst"),
    ("factorielle", "modele_momentum_prix"),
    ("factorielle", "modele_carry_proxy"),
    ("factorielle", "modele_beta_vol"),
    ("risque", "modele_var_drawdown"),
    ("risque", "modele_skew_kurtosis"),
    ("risque", "modele_ratios_performance"),
    ("nlp", "modele_ton_fomc"),
    ("nlp", "modele_frequence_mots_cles_fomc"),
    ("nlp", "modele_complexite_texte_fomc"),
    ("ml", "modele_walkforward_direction"),
    ("ml", "modele_anomalie_multivariee"),
    ("ml", "modele_test_overfitting"),
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
