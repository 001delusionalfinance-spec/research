"""Modele -- decomposition de variance (R² glissant) : quelle part de la variance des
rendements S&P 500 est expliquee par les variations du taux 10 ans, dans le temps.

Complete modele_beta_facteur_macro.py (le COEFFICIENT beta, l'amplitude) avec le R² (la
PUISSANCE EXPLICATIVE, entre 0 et 1) -- un beta peut etre stable alors que le R² s'effondre
(le facteur explique de moins en moins la variance totale, meme avec la meme sensibilite
moyenne). Fenetre glissante 60j, meme regression simple deja utilisee ailleurs.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log  # noqa: E402

NOM_MODELE = "decomposition_variance"
FENETRE = 60


def r2_regression_simple(y: list, x: list) -> float:
    n = min(len(x), len(y))
    if n < 10:
        raise SerieVide("pas assez de points")
    x, y = x[-n:], y[-n:]
    mx, my = sum(x) / n, sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    var_x = sum((xi - mx) ** 2 for xi in x)
    var_y = sum((yi - my) ** 2 for yi in y)
    if var_x == 0 or var_y == 0:
        raise SerieVide("variance nulle -- R2 non defini")
    r = cov / (var_x ** 0.5 * var_y ** 0.5)
    return r ** 2


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        dgs10 = read_series(BRUT / "fred" / "DGS10.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in sp500) & set(d for d, _ in dgs10))
    if len(dates_communes) < FENETRE + 1:
        print("echec -- pas assez de dates communes")
        return 1

    map_sp500, map_dgs10 = dict(sp500), dict(dgs10)
    prix_sp500 = [map_sp500[d] for d in dates_communes]
    niveaux_dgs10 = [map_dgs10[d] for d in dates_communes]

    rendements_sp500 = rendements_log(prix_sp500)
    variations_dgs10 = [b - a for a, b in zip(niveaux_dgs10[:-1], niveaux_dgs10[1:])]

    try:
        r2 = r2_regression_simple(rendements_sp500[-FENETRE:], variations_dgs10[-FENETRE:])
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    date_du_jour = dates_communes[-1]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "r2_sp500_dgs10_60j", "pct_variance_expliquee"],
        [[date_du_jour, round(r2, 5), round(r2 * 100, 2)]],
    )

    print(f"OK -- R² SP500~DGS10 ({FENETRE}j) = {r2:.4f} -- {r2*100:.1f}% de la variance des "
          f"rendements SP500 expliquee par les variations du taux 10 ans (le reste = "
          f"idiosyncratique/autres facteurs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
