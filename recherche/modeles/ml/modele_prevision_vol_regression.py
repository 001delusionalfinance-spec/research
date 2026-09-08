"""Modele -- prevision de volatilite par regression simple (AR(1) sur les rendements au
carre), comparee honnetement a une baseline naive -- pas a GARCH/EWMA directement (ceux-ci
prevoient une VARIANCE LISSEE/conditionnelle, la comparaison directe de MSE contre un rendement
au carre BRUT et tres bruyant ne serait pas equitable pour eux -- cf. limite documentee
ci-dessous).

Split strict train/test (70/30, PAS shuffle -- split temporel simple, coefficients fittes
UNIQUEMENT sur train, jamais re-fittes en voyant le test) : r_t^2 = a + b*r_(t-1)^2, fitte sur
train, evalue sur test contre une baseline "persistance" (predire r_t^2 = r_(t-1)^2, sans
aucun parametre fitte).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs  # noqa: E402

NOM_MODELE = "prevision_vol_regression"
PART_TRAIN = 0.7


def fit_regression_lineaire(x: list, y: list) -> tuple:
    """Retourne (a, b) tel que y ~ a + b*x, moindres carres simples."""
    n = len(x)
    if n < 30:
        raise SerieVide("moins de 30 points -- regression non fiable")
    mx, my = sum(x) / n, sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    var_x = sum((xi - mx) ** 2 for xi in x)
    if var_x == 0:
        raise SerieVide("variance nulle sur x -- regression impossible")
    b = cov / var_x
    a = my - b * mx
    return a, b


def mse(predictions: list, reels: list) -> float:
    n = len(predictions)
    return sum((p - r) ** 2 for p, r in zip(predictions, reels)) / n


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    date_du_jour = sp500[-1][0]
    prix = valeurs(sp500)
    rendements = rendements_log(prix)
    rendements_carres = [r ** 2 for r in rendements]

    if len(rendements_carres) < 200:
        print("echec -- historique insuffisant pour un split train/test fiable")
        return 1

    n_total = len(rendements_carres)
    n_train = int(n_total * PART_TRAIN)

    x_train = rendements_carres[:n_train - 1]
    y_train = rendements_carres[1:n_train]

    try:
        a, b = fit_regression_lineaire(x_train, y_train)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    x_test = rendements_carres[n_train - 1:-1]
    y_test = rendements_carres[n_train:]

    predictions_regression = [a + b * x for x in x_test]
    predictions_naive = list(x_test)  # baseline persistance -- predit r_t^2 = r_(t-1)^2

    mse_regression = mse(predictions_regression, y_test)
    mse_naive = mse(predictions_naive, y_test)
    bat_naive = mse_regression < mse_naive

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_train", "n_test", "coef_a", "coef_b", "mse_regression", "mse_naive",
         "bat_la_baseline"],
        [[date_du_jour, n_train, len(y_test), round(a, 8), round(b, 5),
          round(mse_regression, 10), round(mse_naive, 10), bat_naive]],
    )

    print(f"OK -- regression AR(1) (a={a:.6f}, b={b:.4f}) MSE={mse_regression:.4e} vs "
          f"baseline persistance MSE={mse_naive:.4e} -- "
          f"{'BAT la baseline' if bat_naive else 'NE BAT PAS la baseline'} "
          f"(resultat honnete, pas ajuste)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
