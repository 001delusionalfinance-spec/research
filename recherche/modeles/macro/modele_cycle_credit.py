"""Modele -- cycle du credit US, croissance annuelle du credit bancaire total (TOTBKCR, Fed
H.8, hebdomadaire).

Phase d'expansion/contraction du levier bancaire -- un ralentissement marque de la croissance
du credit precede souvent un ralentissement economique plus large (le credit se resserre avant
que l'activite reelle ne le montre). Pas de comparaison au PIB (aucune serie de PIB ingeree ici,
omission documentee plutot qu'un proxy invente) -- croissance YoY seule, comparee a sa propre
moyenne historique pour juger si elle accelere/ralentit.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, percentile_rang, read_series, valeurs  # noqa: E402

NOM_MODELE = "cycle_credit"


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    if len(serie) < 2:
        raise SerieVide("pas assez de points")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant")
    return candidats[-1]


def croissance_yoy_glissante(serie: list, jours: int = 365, pas_jours: int = 30) -> list:
    """Croissance YoY calculee a intervalles reguliers (pas hebdo, trop de points sinon) sur
    toute la serie disponible -- pour situer la valeur actuelle dans son propre historique."""
    out = []
    dates_serie = [d for d, _ in serie]
    valeurs_serie = dict(serie)
    date_min = date.fromisoformat(dates_serie[0]) + timedelta(days=jours)
    date_max = date.fromisoformat(dates_serie[-1])
    d = date_min
    while d <= date_max:
        d_str = d.isoformat()
        candidats_actuels = [v for dd, v in serie if dd <= d_str]
        candidats_an_dernier = [v for dd, v in serie
                                 if dd <= (d - timedelta(days=jours)).isoformat()]
        if candidats_actuels and candidats_an_dernier:
            croissance = (candidats_actuels[-1] / candidats_an_dernier[-1] - 1) * 100
            out.append(croissance)
        d += timedelta(days=pas_jours)
    return out


def main() -> int:
    try:
        credit = read_series(BRUT / "fred" / "TOTBKCR.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    try:
        credit_an_dernier = valeur_n_jours_avant(credit, 365)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    credit_actuel = credit[-1][1]
    croissance_yoy = (credit_actuel / credit_an_dernier - 1) * 100

    try:
        historique_croissance = croissance_yoy_glissante(credit)
        rang_percentile = percentile_rang(croissance_yoy, historique_croissance)
    except SerieVide:
        rang_percentile = None

    date_du_jour = credit[-1][0]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "credit_bancaire_total", "croissance_yoy_pct", "rang_percentile_historique"],
        [[date_du_jour, credit_actuel, round(croissance_yoy, 3),
          round(rang_percentile, 1) if rang_percentile is not None else ""]],
    )

    lecture = "acceleration" if rang_percentile and rang_percentile > 66 else \
        ("ralentissement" if rang_percentile and rang_percentile < 33 else "normal")
    print(f"OK -- credit bancaire total croissance YoY={croissance_yoy:+.2f}%, "
          f"rang percentile historique={rang_percentile}, lecture={lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
