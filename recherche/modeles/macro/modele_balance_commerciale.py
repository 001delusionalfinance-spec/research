"""Modele -- balance commerciale US (biens+services, BOPGSTB), niveau et tendance.

Desequilibre commercial structurel -- deja negatif depuis des decennies pour les US, donc le
niveau absolu compte moins que la TENDANCE (le deficit se creuse ou se resorbe). Rang
percentile sur l'historique disponible pour situer le niveau actuel.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, percentile_rang, read_series, valeurs  # noqa: E402

NOM_MODELE = "balance_commerciale"


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
        balance = read_series(BRUT / "fred" / "BOPGSTB.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    valeur_actuelle = balance[-1][1]
    date_du_jour = balance[-1][0]
    rang = percentile_rang(valeur_actuelle, valeurs(balance))

    try:
        valeur_an_dernier = valeur_n_jours_avant(balance, 365)
        variation_yoy = valeur_actuelle - valeur_an_dernier
        tendance = "se creuse" if variation_yoy < 0 else ("se resorbe" if variation_yoy > 0 else "stable")
    except SerieVide:
        variation_yoy, tendance = None, "indisponible"

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "balance_millions_usd", "rang_percentile_historique", "variation_yoy",
         "tendance"],
        [[date_du_jour, valeur_actuelle, round(rang, 1),
          round(variation_yoy, 0) if variation_yoy is not None else "", tendance]],
    )

    print(f"OK -- balance commerciale={valeur_actuelle:,.0f}M$ (rang percentile={rang:.0f}), "
          f"deficit {tendance}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
