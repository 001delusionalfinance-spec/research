import csv

from _lib import _indices_cle_naturelle, accumuler_csv


def test_cle_simple_par_date():
    assert _indices_cle_naturelle(["date", "value"], [["2026-01-01", 1]]) == [0]


def test_cle_date_et_horizon_si_lot_multi_dimensionnel():
    lignes = [["2026-01-01", "1m", 1], ["2026-01-01", "3m", 2]]
    assert _indices_cle_naturelle(["date", "horizon", "value"], lignes) == [0, 1]


def test_dimension_connue_retenue_meme_si_le_modele_ecrit_une_ligne_a_la_fois():
    assert _indices_cle_naturelle(
        ["date", "contrat", "value"], [["2026-01-01", "SOFR_3M", 1]]) == [0, 1]


def test_cle_identifiant_avant_date():
    lignes = [["US", "2026-01-01", 1], ["EA", "2026-01-01", 2]]
    assert _indices_cle_naturelle(["bloc", "date", "value"], lignes) == [0, 1]


def test_upsert_remplace_et_nettoie_les_doublons(tmp_path):
    chemin = tmp_path / "etat.csv"
    chemin.write_text("date,value\n2026-01-01,ancien\n2026-01-01,corrige\n", encoding="utf-8")

    accumuler_csv(chemin, ["date", "value"], [["2026-01-01", "final"]])

    with chemin.open(encoding="utf-8", newline="") as f:
        assert list(csv.reader(f)) == [["date", "value"], ["2026-01-01", "final"]]


def test_upsert_preserve_l_historique(tmp_path):
    chemin = tmp_path / "etat.csv"
    accumuler_csv(chemin, ["date", "value"], [["2026-01-01", 1]])
    accumuler_csv(chemin, ["date", "value"], [["2026-01-02", 2]])

    with chemin.open(encoding="utf-8", newline="") as f:
        assert list(csv.reader(f)) == [
            ["date", "value"], ["2026-01-01", "1"], ["2026-01-02", "2"]]
