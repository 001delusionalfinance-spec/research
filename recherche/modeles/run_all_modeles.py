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
    ("macro", "modele_regle_taylor"),
    ("macro", "modele_courbe_taux_us"),
    ("macro", "modele_cycle_credit"),
    ("macro", "modele_conditions_financieres"),
    ("positionnement-comportemental", "modele_positionnement_cot"),
    ("positionnement-comportemental", "modele_momentum_positionnement"),
    ("positionnement-comportemental", "modele_crowding_cross_asset"),
    ("positionnement-comportemental", "modele_divergence_cot_prix"),
    ("positionnement-comportemental", "modele_ratio_commercial_speculatif"),
    ("positionnement-comportemental", "modele_rotation_risk_on_off"),
    ("positionnement-comportemental", "modele_concentration_traders"),
    ("statistique", "modele_correlations_positionnement"),
    ("statistique", "modele_stationnarite_taux"),
    ("statistique", "modele_correlation_glissante"),
    ("statistique", "modele_cointegration_taux"),
    ("statistique", "modele_pca_taux"),
    ("statistique", "modele_clustering_marches"),
    ("statistique", "modele_causalite_granger"),
    ("series-temporelles", "modele_volatilite_ewma"),
    ("series-temporelles", "modele_garch"),
    ("series-temporelles", "modele_hurst"),
    ("series-temporelles", "modele_ornstein_uhlenbeck_vix"),
    ("series-temporelles", "modele_changepoint_volatilite"),
    ("series-temporelles", "modele_kalman_niveau_local"),
    ("series-temporelles", "modele_hp_filter_taux"),
    ("factorielle", "modele_momentum_prix"),
    ("factorielle", "modele_carry_proxy"),
    ("factorielle", "modele_beta_vol"),
    ("factorielle", "modele_rotation_sectorielle"),
    ("factorielle", "modele_saisonnalite"),
    ("factorielle", "modele_dispersion_sectorielle"),
    ("factorielle", "modele_low_volatility"),
    ("risque", "modele_var_drawdown"),
    ("risque", "modele_skew_kurtosis"),
    ("risque", "modele_ratios_performance"),
    ("risque", "modele_covar"),
    ("risque", "modele_stress_test_historique"),
    ("risque", "modele_sizing_robuste"),
    ("risque", "modele_nombre_effectif_paris"),
    ("nlp", "modele_ton_fomc"),
    ("nlp", "modele_frequence_mots_cles_fomc"),
    ("nlp", "modele_complexite_texte_fomc"),
    ("nlp", "modele_ton_minutes_fomc"),
    ("nlp", "modele_ecart_communique_minutes"),
    ("nlp", "modele_complexite_texte_minutes"),
    ("nlp", "modele_entites_geographiques_minutes"),
    ("ml", "modele_walkforward_direction"),
    ("ml", "modele_anomalie_multivariee"),
    ("ml", "modele_test_overfitting"),
    ("ml", "modele_prevision_vol_regression"),
    ("ml", "modele_kmeans_regimes"),
    ("ml", "modele_ensemble_signaux"),
    ("ml", "modele_screening_features"),
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
