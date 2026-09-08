"""Modele -- regression lineaire multi-features (momentum 5j + variation VIX) sur le rendement
J+1 du S&P 500 -- suite logique de modele_screening_features.py (screening univarie) et
modele_prevision_vol_regression.py (regression a 1 feature) : ici, 2 features ENSEMBLE dans une
seule regression, pas testees separement.

Split train/test strict 70/30 (temporel, pas shuffle), coefficients fittes uniquement sur
train. Compare le R² out-of-sample a zero (un R² negatif hors echantillon signifie que le
modele fait PIRE que predire la moyenne -- resultat possible et a rapporter tel quel, pas un
bug).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log  # noqa: E402

NOM_MODELE = "regression_multifeatures"
FENETRE_MOMENTUM = 5
PART_TRAIN = 0.7


def fit_ols_2_features(y: list, x1: list, x2: list) -> tuple:
    """Regression y ~ a + b1*x1 + b2*x2, moindres carres via l'algebre matricielle numpy --
    2 features, pas la peine de reimplementer une descente de gradient a la main."""
    import numpy as np
    n = len(y)
    if n < 30:
        raise SerieVide("moins de 30 points")
    X = np.column_stack([np.ones(n), x1, x2])
    Y = np.array(y)
    coeffs, *_ = np.linalg.lstsq(X, Y, rcond=None)
    return coeffs[0], coeffs[1], coeffs[2]


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in sp500) & set(d for d, _ in vix))
    if len(dates_communes) < 300:
        print("echec -- moins de 300 dates communes")
        return 1

    map_sp500, map_vix = dict(sp500), dict(vix)
    prix = [map_sp500[d] for d in dates_communes]
    niveaux_vix = [map_vix[d] for d in dates_communes]
    date_du_jour = dates_communes[-1]

    rendements = rendements_log(prix)
    variations_vix = [b - a for a, b in zip(niveaux_vix[:-1], niveaux_vix[1:])]

    # features connues au moment i (avant de predire rendements[i]) : momentum sur prix[0..i],
    # variation vix du jour i-1 -> i (deja dans le passe au moment de predire le rendement de
    # dates[i+1])
    n = len(rendements)
    y, x1, x2 = [], [], []
    for i in range(FENETRE_MOMENTUM, n):
        momentum = (prix[i] - prix[i - FENETRE_MOMENTUM]) / prix[i - FENETRE_MOMENTUM]
        y.append(rendements[i])
        x1.append(momentum)
        x2.append(variations_vix[i - 1] if i - 1 < len(variations_vix) else 0.0)

    n_total = len(y)
    n_train = int(n_total * PART_TRAIN)
    if n_train < 30 or n_total - n_train < 30:
        print("echec -- split train/test insuffisant")
        return 1

    try:
        a, b1, b2 = fit_ols_2_features(y[:n_train], x1[:n_train], x2[:n_train])
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    y_test = y[n_train:]
    predictions_test = [a + b1 * x1[n_train + i] + b2 * x2[n_train + i]
                         for i in range(len(y_test))]

    moyenne_test = sum(y_test) / len(y_test)
    sse_modele = sum((p - r) ** 2 for p, r in zip(predictions_test, y_test))
    sse_moyenne = sum((moyenne_test - r) ** 2 for r in y_test)
    r2_oos = 1 - sse_modele / sse_moyenne if sse_moyenne > 0 else None

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "coef_intercept", "coef_momentum5j", "coef_variation_vix", "n_train",
         "n_test", "r2_out_of_sample"],
        [[date_du_jour, round(a, 6), round(b1, 6), round(b2, 6), n_train, len(y_test),
          round(r2_oos, 5) if r2_oos is not None else ""]],
    )

    print(f"OK -- coefs (intercept={a:.5f}, momentum5j={b1:.4f}, var_vix={b2:.5f}) -- "
          f"R2 out-of-sample={r2_oos:.4f} "
          f"({'modele bat la moyenne' if r2_oos and r2_oos > 0 else 'modele NE BAT PAS la moyenne (R2<=0)'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
