from pathlib import Path

import _lib
import generer_visualisations as visualisations


RACINE = Path(__file__).resolve().parents[1]


def test_rapports_est_l_unique_emplacement_des_sorties():
    assert _lib.ETAT == RACINE / "rapports" / "donnees"
    assert _lib.VISUALISATIONS == RACINE / "rapports" / "graphiques"
    assert not (RACINE / "recherche" / "etat").exists()
    assert not (RACINE / "recherche" / "visualisations").exists()
    assert not (RACINE / "rapports" / "fed").exists()


def test_la_selection_graphique_ne_couvre_que_des_csv_existants():
    for nom, config in visualisations.CONFIG_GRAPHIQUES.items():
        chemin = _lib.ETAT / f"{nom}.csv"
        entete, _ = visualisations._lire(chemin)
        assert set(config["colonnes"]).issubset(entete)
        if config["mode"] == "comparaison":
            assert config["etiquette"] in entete


def test_les_sorties_textuelles_et_de_controle_restent_en_csv():
    selection = set(visualisations.CONFIG_GRAPHIQUES)
    assert {"ton_fomc", "lisibilite_flesch_kincaid", "coherence_fed"}.isdisjoint(selection)


def test_les_figures_metier_ne_sont_pas_dupliquees_par_un_apercu_generique():
    selection = set(visualisations.CONFIG_GRAPHIQUES)
    assert {
        "positionnement_cot", "correlation_glissante", "regime_monetaire_emploi",
        "volatilite_ewma",
    }.isdisjoint(selection)
