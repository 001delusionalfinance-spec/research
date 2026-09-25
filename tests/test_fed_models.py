from controle_coherence_fed import milieu_fourchette
from modele_chemin_taux_fed import lecture, taux_forward


def test_milieu_fourchette_fractionnaire():
    assert milieu_fourchette("3-3/4 to 4") == 3.875


def test_forward_simple():
    assert taux_forward(0.25, 4.0, 0.5, 4.5) == 5.0


def test_lecture_ne_promet_pas_une_probabilite():
    assert lecture(4.9) == "statu quo"
    assert lecture(6) == "hausse"
    assert lecture(-6) == "baisse"
