import csv
from datetime import date, timedelta

import controle_fraicheur as fraicheur


def _serie_quotidienne(chemin, derniere_date):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8", newline="") as flux:
        ecrivain = csv.writer(flux)
        ecrivain.writerow(["date", "valeur"])
        for recul in range(30, -1, -1):
            ecrivain.writerow([(derniere_date - timedelta(days=recul)).isoformat(), "1"])


def test_un_fichier_quotidien_ordinaire_devient_suspect_apres_21_jours(tmp_path, monkeypatch):
    monkeypatch.setattr(fraicheur, "BRUT_DIR", tmp_path)
    chemin = tmp_path / "source" / "serie.csv"
    _serie_quotidienne(chemin, date.today() - timedelta(days=25))
    assert fraicheur.analyser(chemin)["verdict"] == "SUSPECTE"


def test_le_lot_mensuel_mof_n_est_pas_un_faux_positif(tmp_path, monkeypatch):
    monkeypatch.setattr(fraicheur, "BRUT_DIR", tmp_path)
    chemin = tmp_path / "souverains" / "JAPON_10A.csv"
    _serie_quotidienne(chemin, date.today() - timedelta(days=25))
    resultat = fraicheur.analyser(chemin)
    assert resultat["verdict"] == "OK"
    assert resultat["seuil_gele_jours"] == 90


def test_le_retard_habituel_bis_coree_n_est_pas_un_faux_positif(tmp_path, monkeypatch):
    monkeypatch.setattr(fraicheur, "BRUT_DIR", tmp_path)
    chemin = tmp_path / "bis" / "taux_directeurs" / "KR.csv"
    _serie_quotidienne(chemin, date.today() - timedelta(days=28))
    assert fraicheur.analyser(chemin)["verdict"] == "OK"
