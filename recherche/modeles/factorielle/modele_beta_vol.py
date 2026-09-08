"""Modele -- beta glissant du S&P 500 au VIX ("vol-beta"), fenetre 60j.

Exposition factorielle au facteur volatilite : combien le S&P bouge-t-il (en rendement) pour
1 point de variation du VIX ? Regression simple rendement_SP500 ~ variation_VIX sur fenetre
glissante -- un beta qui devient plus negatif = le marche devient plus reactif a la vol
(regime plus fragile), pas juste "la correlation est negative" (deja mesure par
correlation_glissante.py) mais la SENSIBILITE (l'amplitude du mouvement, pas seulement son
signe).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log  # noqa: E402

NOM_MODELE = "beta_vol"
FENETRE = 60


def beta_regression(y: list, x: list) -> float:
    """Beta de y sur x -- cov(x,y)/var(x), regression lineaire simple sans intercept."""
    n = min(len(x), len(y))
    if n < 3:
        raise SerieVide("pas assez de points pour une regression")
    x, y = x[-n:], y[-n:]
    mx, my = sum(x) / n, sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    var_x = sum((xi - mx) ** 2 for xi in x)
    if var_x == 0:
        raise SerieVide("variance nulle sur le VIX -- beta non defini")
    return cov / var_x


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in sp500) & set(d for d, _ in vix))
    if len(dates_communes) < FENETRE + 1:
        print("echec -- pas assez de dates communes")
        return 1

    map_sp500, map_vix = dict(sp500), dict(vix)
    prix_sp500 = [map_sp500[d] for d in dates_communes]
    prix_vix = [map_vix[d] for d in dates_communes]

    rendements_sp500 = rendements_log(prix_sp500)
    variations_vix = [b - a for a, b in zip(prix_vix[:-1], prix_vix[1:])]  # variation en points,
                                                                             # pas en rendement --
                                                                             # le VIX est deja
                                                                             # une vol, pas un prix

    try:
        beta = beta_regression(rendements_sp500[-FENETRE:], variations_vix[-FENETRE:])
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    date_du_jour = dates_communes[-1]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "beta_sp500_vix_60j"],
        [[date_du_jour, round(beta, 6)]],
    )

    print(f"OK -- beta SP500/VIX ({FENETRE}j) = {beta:.5f} (rendement SP500 pour +1pt VIX)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
