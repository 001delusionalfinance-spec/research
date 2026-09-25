import csv
from datetime import date, timedelta

import publier_rapports as publication
from run_all_modeles import MODELES


def test_tous_les_modeles_ont_exactement_un_theme():
    publication.verifier_couverture()
    classes = [publication.theme_du_modele(publication.nom_court(nom)) for _, nom in MODELES]
    assert len(classes) == len(MODELES) == 112
    assert len(set(classes)) == len(publication.THEMES)


def test_les_themes_sont_economiques_et_non_les_repertoires_techniques():
    assert publication.theme_du_modele("regle_taylor") == "banques-centrales"
    assert publication.theme_du_modele("ton_fomc") == "banques-centrales"
    assert publication.theme_du_modele("garch") == "risques-regimes"
    assert publication.theme_du_modele("kmeans_regimes") == "modeles-validation"


def test_derniere_observation_ignore_une_date_future(tmp_path):
    chemin = tmp_path / "sortie.csv"
    passe = date.today() - timedelta(days=2)
    futur = date.today() + timedelta(days=30)
    with chemin.open("w", encoding="utf-8", newline="") as flux:
        ecrivain = csv.writer(flux)
        ecrivain.writerow(["date_calcul", "prochaine_reunion", "valeur"])
        ecrivain.writerow([passe.isoformat(), futur.isoformat(), "1"])
    assert publication._derniere_observation(chemin) == passe.isoformat()


def test_derniere_observation_comprend_les_dates_compactes(tmp_path):
    chemin = tmp_path / "nlp.csv"
    with chemin.open("w", encoding="utf-8", newline="") as flux:
        ecrivain = csv.writer(flux)
        ecrivain.writerow(["institution", "document"])
        ecrivain.writerow(["Fed", "20260916"])
        ecrivain.writerow(["BCE", "declaration_2026-09-10"])
    assert publication._derniere_observation(chemin) == "2026-09-16"


def test_les_sorties_renommees_restent_retrouvables():
    assert publication.SORTIES_SPECIALES["walkforward_direction"] == (
        "walkforward_direction_sp500"
    )
    assert publication.SORTIES_SPECIALES["test_overfitting"] == (
        "test_overfitting_momentum"
    )


def test_relecture_du_rapport_thematise_est_idempotente(tmp_path, monkeypatch):
    rapport = tmp_path / "lecture-du-jour.md"
    rapport.write_text(
        "# Rapport global\n\n"
        "## [Banques centrales](themes/banques-centrales.md)\n\n"
        "- **Regle taylor** — lecture courante _(observation : 2026-09-24)_\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(publication, "RAPPORTS", tmp_path)
    lectures = publication._lire_lecture()
    assert lectures["regle_taylor"]["lecture"] == "lecture courante"
    assert lectures["regle_taylor"]["lane"] == "macro"
