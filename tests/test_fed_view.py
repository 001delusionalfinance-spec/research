from construire_vue_fed import construire_sections


def test_vue_fed_a_cinq_sections_et_des_identifiants_uniques():
    sections = construire_sections()
    assert [section["id"] for section in sections] == [
        "position_actuelle",
        "fonction_reaction",
        "anticipations_marche",
        "liquidite_bilan",
        "communication",
    ]
    identifiants = [m["id"] for section in sections for m in section["metrics"]]
    assert len(identifiants) == len(set(identifiants))
    assert "fed_target_midpoint" in identifiants
    assert any(identifiant.startswith("rate_path_") for identifiant in identifiants)
