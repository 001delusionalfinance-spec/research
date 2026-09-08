"""Modele -- taux de change effectif reel US (REER, BIS, serie RBUSBIS), niveau et tendance.

Contrairement a USD_INDEX (deja suivi via le positionnement COT), le REER BIS pondere le dollar
contre un panier large de partenaires commerciaux et AJUSTE de l'inflation relative -- mesure
la competitivite reelle, pas juste le prix nominal du dollar. Base 100 = 2020 (convention BIS).
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, percentile_rang, read_series, valeurs  # noqa: E402

NOM_MODELE = "reer_us"


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    if len(serie) < 2:
        raise SerieVide("pas assez de points")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant")
    return candidats[-1]


def main() -> int:
    try:
        reer = read_series(BRUT / "fred" / "RBUSBIS.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    valeur_actuelle = reer[-1][1]
    date_du_jour = reer[-1][0]
    rang = percentile_rang(valeur_actuelle, valeurs(reer))

    try:
        valeur_an_dernier = valeur_n_jours_avant(reer, 365)
        variation_yoy = (valeur_actuelle / valeur_an_dernier - 1) * 100
    except SerieVide:
        variation_yoy = None

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "reer_niveau", "rang_percentile_historique", "variation_yoy_pct"],
        [[date_du_jour, valeur_actuelle, round(rang, 1),
          round(variation_yoy, 2) if variation_yoy is not None else ""]],
    )

    lecture = "fort (competitivite reduite)" if rang > 66 else \
        ("faible (competitivite accrue)" if rang < 33 else "moyen")
    variation_str = f"{variation_yoy:+.2f}%" if variation_yoy is not None else "indisponible"
    print(f"OK -- REER US={valeur_actuelle:.2f} (rang percentile={rang:.0f}, "
          f"variation YoY={variation_str}) -- dollar reel {lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
