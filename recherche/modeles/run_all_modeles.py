"""Orchestrateur -- appelle main() de chaque modele en sequence, un modele casse n'interrompt
jamais les autres (meme discipline que global-macro-desk-cloud).

Usage :
    python run_all_modeles.py
"""

import contextlib
import importlib
import io
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ICI = Path(__file__).resolve().parent
REPO_ROOT = ICI.parents[1]

MODELES = [
    ("macro", "modele_regime_monetaire_emploi"),
    ("macro", "modele_sahm_rule"),
    ("macro", "modele_taux_reel_us"),
    ("macro", "modele_regle_taylor"),
    ("macro", "modele_courbe_taux_us"),
    ("macro", "modele_probabilite_reunion_fed"),
    ("macro", "modele_cycle_credit"),
    ("macro", "modele_conditions_financieres"),
    ("macro", "modele_reer_us"),
    ("macro", "modele_cycle_immobilier"),
    # --- Modeles ajoutes le 2026-09-14 : ils lisent les donnees ingerees le meme jour
    #     (prix BIS, taux directeurs quotidiens, bilans, Eurostat, service de la dette).
    #     Jusque-la ces donnees etaient ingerees sans qu'aucun modele ne les ouvre.
    ("macro", "modele_inflation_comparee"),
    ("macro", "modele_divergence_taux_directeurs"),
    ("macro", "modele_bilans_banques_centrales"),
    ("macro", "modele_liquidite_nette_fed"),
    ("macro", "modele_activite_zone_euro"),
    ("macro", "modele_soutenabilite_dette"),
    ("macro", "modele_matieres_premieres_macro"),
    ("macro", "modele_emission_tresor_us"),
    ("series-temporelles", "modele_pentes_courbes"),
    ("statistique", "modele_differentiel_taux_change"),
    ("factorielle", "modele_indices_mondiaux"),
    ("risque", "modele_vol_cross_asset"),
    ("positionnement-comportemental", "modele_positionnement_courbe_taux"),
    ("positionnement-comportemental", "modele_positionnement_devises"),
    ("nlp", "modele_ton_banques_centrales"),
    ("positionnement-comportemental", "modele_positionnement_cot"),
    ("positionnement-comportemental", "modele_momentum_positionnement"),
    ("positionnement-comportemental", "modele_crowding_cross_asset"),
    ("positionnement-comportemental", "modele_divergence_cot_prix"),
    ("positionnement-comportemental", "modele_ratio_commercial_speculatif"),
    ("positionnement-comportemental", "modele_rotation_risk_on_off"),
    ("positionnement-comportemental", "modele_concentration_traders"),
    ("positionnement-comportemental", "modele_metaux_precieux"),
    ("positionnement-comportemental", "modele_persistance_extremes"),
    ("statistique", "modele_correlations_positionnement"),
    ("statistique", "modele_stationnarite_taux"),
    ("statistique", "modele_correlation_glissante"),
    ("statistique", "modele_cointegration_taux"),
    ("statistique", "modele_pca_taux"),
    ("statistique", "modele_clustering_marches"),
    ("statistique", "modele_causalite_granger"),
    ("statistique", "modele_dependance_queue"),
    ("statistique", "modele_beta_facteur_macro"),
    ("series-temporelles", "modele_volatilite_ewma"),
    ("series-temporelles", "modele_garch"),
    ("series-temporelles", "modele_hurst"),
    ("series-temporelles", "modele_ornstein_uhlenbeck_vix"),
    ("series-temporelles", "modele_changepoint_volatilite"),
    ("series-temporelles", "modele_kalman_niveau_local"),
    ("series-temporelles", "modele_hp_filter_taux"),
    ("series-temporelles", "modele_var_sp500_vix"),
    ("series-temporelles", "modele_analyse_spectrale"),
    ("factorielle", "modele_momentum_prix"),
    ("factorielle", "modele_carry_proxy"),
    ("factorielle", "modele_beta_vol"),
    ("factorielle", "modele_rotation_sectorielle"),
    ("factorielle", "modele_saisonnalite"),
    ("factorielle", "modele_dispersion_sectorielle"),
    ("factorielle", "modele_low_volatility"),
    ("factorielle", "modele_facteur_qualite_credit"),
    ("factorielle", "modele_momentum_cross_sectional"),
    ("risque", "modele_var_drawdown"),
    ("risque", "modele_skew_kurtosis"),
    ("risque", "modele_ratios_performance"),
    ("risque", "modele_covar"),
    ("risque", "modele_stress_test_historique"),
    ("risque", "modele_sizing_robuste"),
    ("risque", "modele_nombre_effectif_paris"),
    ("risque", "modele_detection_saut"),
    ("risque", "modele_choc_taux"),
    ("nlp", "modele_ton_fomc"),
    ("nlp", "modele_frequence_mots_cles_fomc"),
    ("nlp", "modele_complexite_texte_fomc"),
    ("nlp", "modele_ton_minutes_fomc"),
    ("nlp", "modele_ecart_communique_minutes"),
    ("nlp", "modele_complexite_texte_minutes"),
    ("nlp", "modele_entites_geographiques_minutes"),
    ("nlp", "modele_similarite_vocabulaire_minutes"),
    ("nlp", "modele_lisibilite_flesch_kincaid"),
    ("ml", "modele_walkforward_direction"),
    ("ml", "modele_anomalie_multivariee"),
    ("ml", "modele_test_overfitting"),
    ("ml", "modele_prevision_vol_regression"),
    ("ml", "modele_kmeans_regimes"),
    ("ml", "modele_ensemble_signaux"),
    ("ml", "modele_screening_features"),
    ("ml", "modele_couts_transaction"),
    ("ml", "modele_regression_multifeatures"),
    ("macro", "modele_surprise_macro_composite"),
    ("macro", "modele_balance_commerciale"),
    ("macro", "modele_surprise_inflation"),
    ("positionnement-comportemental", "modele_dollar_smile"),
    ("positionnement-comportemental", "modele_extremes_historiques"),
    ("positionnement-comportemental", "modele_correlation_cot_prix"),
    ("statistique", "modele_decomposition_variance"),
    ("statistique", "modele_test_chow"),
    ("statistique", "modele_cointegration_secteurs"),
    ("series-temporelles", "modele_arima"),
    ("factorielle", "modele_qualite_regime_macro"),
    ("risque", "modele_var_conditionnelle_regime"),
    ("ml", "modele_stacking"),
    ("series-temporelles", "modele_decomposition_stl"),
    ("series-temporelles", "modele_ornstein_uhlenbeck_credit"),
    ("factorielle", "modele_momentum_credit"),
    ("factorielle", "modele_correlation_facteurs"),
    ("risque", "modele_ratios_conditionnels_regime"),
    ("risque", "modele_choc_vol_parametrique"),
    ("nlp", "modele_frequence_mots_cles_minutes"),
    ("nlp", "modele_langage_prudence"),
    ("nlp", "modele_intensite_desaccord"),
    ("ml", "modele_decision_stump"),
    ("ml", "modele_importance_permutation"),
]


def _lecture(sortie: str) -> tuple:
    """Extrait la phrase interpretable d'un modele. Retourne (texte, conforme).

    Convention du depot : un modele termine par une ligne "OK -- ..." ou "echec -- ..." ecrite
    pour etre comprise sans lire le code.

    Douze modeles ne la respectent pas (constate le 2026-09-14) : ils ENUMERENT sans conclure --
    une ligne par pays, par contrat ou par paire, et rien qui resume. Pour eux on retombe sur la
    derniere ligne utile, mais le drapeau `conforme` reste faux et le rapport les signale. Les
    masquer aurait produit une premiere page d'apparence complete ou douze entrees seraient en
    realite un item pris au hasard dans une liste.
    """
    lignes = [l.strip() for l in sortie.splitlines() if l.strip()]
    if not lignes:
        return "(aucune sortie)", False

    for i, ligne in enumerate(lignes):
        if ligne.startswith(("OK --", "echec --")):
            # Certaines lectures sont un en-tete suivi du detail ("... 4 clusters :").
            # Dans ce cas on rattache les lignes suivantes, sinon la lecture ne dit rien.
            if ligne.endswith(":"):
                suite = " | ".join(lignes[i + 1:i + 6])
                return (ligne + " " + suite).strip(), True
            return ligne, True

    # Repli : une ligne de synthese chiffree ("1/10 paires cointegrees") si elle existe,
    # sinon la derniere ligne affichee.
    for ligne in reversed(lignes):
        if re.match(r"^\d+\s*/\s*\d+", ligne):
            return ligne, False
    return lignes[-1], False


def _ecrire_rapport(resultats: list) -> Path:
    """Ecrit rapports/lecture-du-jour.md -- la premiere page du dispositif.

    Raison d'etre : les modeles produisent chacun une lecture en langage clair, mais elle
    n'existait que dans le journal d'execution et disparaissait apres le run. Personne ne
    lisait cent fichiers d'etat un par un. Sans cette page, le depot calculait beaucoup et ne
    disait rien.
    """
    rapport = REPO_ROOT / "rapports" / "lecture-du-jour.md"
    rapport.parent.mkdir(parents=True, exist_ok=True)
    horodatage = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    en_echec = [r for r in resultats if not r["ok"]]

    lignes = [f"# Lecture du jour -- {horodatage}", "",
              f"{len(resultats) - len(en_echec)} modeles sur {len(resultats)} ont produit une "
              f"lecture.", ""]
    non_conformes = [r for r in resultats if r["ok"] and not r["conforme"]]
    if non_conformes:
        lignes += ["> " + str(len(non_conformes)) + " modele(s) n'ont **pas de ligne de "
                   "synthese** : ils enumerent sans conclure. La lecture affichee pour eux est "
                   "un repli sur leur derniere ligne, elle est signalee par _(sans synthese)_ "
                   "et ne resume pas l'ensemble de leur sortie.", ""]
    if en_echec:
        lignes += ["**" + str(len(en_echec)) + " en echec** : "
                   + ", ".join("`" + r["lane"] + "/" + r["nom"] + "`" for r in en_echec), ""]

    for lane in sorted({r["lane"] for r in resultats}):
        lignes += ["## " + lane, ""]
        for r in [x for x in resultats if x["lane"] == lane]:
            texte = r["lecture"]
            for prefixe in ("OK -- ", "echec -- "):
                if texte.startswith(prefixe):
                    texte = texte[len(prefixe):]
            marque = "" if r["ok"] else "**[ECHEC]** "
            suffixe = "" if r["conforme"] else "  _(sans synthese)_"
            lignes.append("- **" + r["nom"].replace("modele_", "") + "** -- " + marque
                          + texte + suffixe)
        lignes.append("")

    rapport.write_text(chr(10).join(lignes), encoding="utf-8")
    return rapport


def main() -> int:
    echecs, resultats = [], []
    for lane, nom in MODELES:
        print(f"\n--- {lane}/{nom} ---")
        sys.path.insert(0, str(ICI / lane))
        tampon = io.StringIO()
        ok = True
        try:
            module = importlib.import_module(nom)
            # Sortie capturee POUR LE RAPPORT puis reaffichee telle quelle : le journal
            # d'execution reste identique, on ne perd rien en diagnostic.
            with contextlib.redirect_stdout(tampon):
                code = module.main()
            if code != 0:
                ok = False
        except Exception as e:
            tampon.write("echec -- exception non geree : " + str(e) + chr(10))
            ok = False
        finally:
            sys.path.remove(str(ICI / lane))

        sortie = tampon.getvalue()
        print(sortie, end="")
        if not ok:
            echecs.append(f"{lane}/{nom}")
        texte, conforme = _lecture(sortie)
        resultats.append({"lane": lane, "nom": nom, "ok": ok,
                          "lecture": texte, "conforme": conforme})

    rapport = _ecrire_rapport(resultats)
    print(f"\n=== Resume : {len(MODELES) - len(echecs)}/{len(MODELES)} modeles OK ===")
    print(f"Lecture du jour -> {rapport}")
    if echecs:
        print(f"En echec : {echecs}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
