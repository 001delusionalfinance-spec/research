"""Modele -- taux directeur reel US (Fed funds nominal - inflation CPI en glissement annuel).

Distinction macro classique : un taux nominal de 3,63% n'est "restrictif" que si l'inflation
est plus basse -- le taux REEL (ex ante idealement via breakeven, ici ex post via CPI realise
faute de source breakeven ingeree) mesure la condition monetaire effective. Limite assumee :
CPI realise, pas anticipe -- un vrai taux reel ex ante utiliserait les breakevens (T10YIE, deja
dans GMDC mais pas encore ici), a ajouter si utile.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "taux_reel_us"


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    if len(serie) < 2:
        raise SerieVide("pas assez de points pour comparer a n jours avant")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant la derniere date")
    return candidats[-1]


def main() -> int:
    try:
        dff = read_series(BRUT / "fred" / "DFF.csv")
        cpi = read_series(BRUT / "fred" / "CPIAUCSL.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    try:
        cpi_an_dernier = valeur_n_jours_avant(cpi, 365)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    cpi_actuel = cpi[-1][1]
    inflation_yoy_pct = (cpi_actuel / cpi_an_dernier - 1) * 100
    taux_nominal = dff[-1][1]
    taux_reel = taux_nominal - inflation_yoy_pct

    date_du_jour = dff[-1][0]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "taux_nominal_pct", "inflation_yoy_pct", "taux_reel_pct"],
        [[date_du_jour, round(taux_nominal, 3), round(inflation_yoy_pct, 3),
          round(taux_reel, 3)]],
    )

    print(f"OK -- nominal={taux_nominal:.2f}%, inflation YoY={inflation_yoy_pct:.2f}%, "
          f"reel={taux_reel:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
