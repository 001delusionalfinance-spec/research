from pathlib import Path


RACINE = Path(__file__).resolve().parents[1]
WORKFLOWS = RACINE / ".github" / "workflows"
CHAINE_HORAIRE = WORKFLOWS / "recherche-modeles.yml"
SURVEILLANCE = WORKFLOWS / "recherche-surveillance.yml"


def test_seules_la_chaine_et_sa_surveillance_sont_planifiees():
    planifies = []
    for chemin in WORKFLOWS.glob("recherche-*.yml"):
        if "schedule:" in chemin.read_text(encoding="utf-8"):
            planifies.append(chemin.name)
    assert sorted(planifies) == ["recherche-modeles.yml", "recherche-surveillance.yml"]


def test_la_chaine_complete_tourne_toutes_les_heures():
    contenu = CHAINE_HORAIRE.read_text(encoding="utf-8")
    assert 'cron: "17,47 * * * *"' in contenu
    assert "ingestion_marches.py" in contenu
    assert "ingestion_cftc.py" in contenu
    assert "ingestion_fred.py" in contenu
    assert "run_all_modeles.py" in contenu
    assert "publier_rapports.py" in contenu
    assert "git add donnees/brut rapports" in contenu


def test_les_ingestions_ciblees_restent_relancables_manuellement():
    specialises = [
        "recherche-ingestion.yml",
        "recherche-ingestion-marches.yml",
        "recherche-ingestion-cot.yml",
    ]
    for nom in specialises:
        contenu = (WORKFLOWS / nom).read_text(encoding="utf-8")
        assert "workflow_dispatch:" in contenu
        assert "schedule:" not in contenu


def test_la_surveillance_rattrape_un_cycle_absent_sans_recalculer():
    contenu = SURVEILLANCE.read_text(encoding="utf-8")
    assert 'cron: "*/5 * * * *"' in contenu
    assert 'age" -ge 3000' in contenu
    assert "gh workflow run recherche-modeles.yml" in contenu
    assert "run_all_modeles.py" not in contenu
