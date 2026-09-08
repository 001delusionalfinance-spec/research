"""Modele -- importance de feature par permutation, sur le modele deja fitte de
modele_regression_multifeatures.py -- POURQUOI le modele predit, pas seulement QUOI (screening
univarie deja fait separement, ici on mesure l'importance DANS le modele combine, effets
partages/redondants entre features inclus).

Methode standard (Breiman 2001, generalisee au-dela des forets aleatoires) : melange
aleatoirement une feature a la fois dans le test set, mesure de combien le R2 out-of-sample se
degrade -- une feature "importante" degrade fortement le R2 quand on detruit son information ;
une feature inutile ne change presque rien.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log  # noqa: E402

NOM_MODELE = "importance_permutation"
FENETRE_MOMENTUM = 5
PART_TRAIN = 0.7
GRAINE = 42


def fit_ols_2_features(y: list, x1: list, x2: list) -> tuple:
    import numpy as np
    n = len(y)
    X = np.column_stack([np.ones(n), x1, x2])
    Y = np.array(y)
    coeffs, *_ = np.linalg.lstsq(X, Y, rcond=None)
    return coeffs[0], coeffs[1], coeffs[2]


def r2_score(predictions: list, reels: list) -> float:
    moyenne = sum(reels) / len(reels)
    sse = sum((p - r) ** 2 for p, r in zip(predictions, reels))
    sst = sum((moyenne - r) ** 2 for r in reels)
    return 1 - sse / sst if sst > 0 else None


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

    a, b1, b2 = fit_ols_2_features(y[:n_train], x1[:n_train], x2[:n_train])

    x1_test, x2_test, y_test = x1[n_train:], x2[n_train:], y[n_train:]
    predictions_base = [a + b1 * xi1 + b2 * xi2 for xi1, xi2 in zip(x1_test, x2_test)]
    r2_base = r2_score(predictions_base, y_test)
    if r2_base is None:
        print("echec -- R2 de base non defini")
        return 1

    rng = random.Random(GRAINE)
    x1_permute = list(x1_test)
    rng.shuffle(x1_permute)
    predictions_sans_x1 = [a + b1 * xi1 + b2 * xi2 for xi1, xi2 in zip(x1_permute, x2_test)]
    r2_sans_x1 = r2_score(predictions_sans_x1, y_test)

    x2_permute = list(x2_test)
    rng.shuffle(x2_permute)
    predictions_sans_x2 = [a + b1 * xi1 + b2 * xi2 for xi1, xi2 in zip(x1_test, x2_permute)]
    r2_sans_x2 = r2_score(predictions_sans_x2, y_test)

    importance_momentum = r2_base - r2_sans_x1 if r2_sans_x1 is not None else None
    importance_vix = r2_base - r2_sans_x2 if r2_sans_x2 is not None else None

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "r2_base", "importance_momentum5j", "importance_variation_vix"],
        [[date_du_jour, round(r2_base, 5),
          round(importance_momentum, 5) if importance_momentum is not None else "",
          round(importance_vix, 5) if importance_vix is not None else ""]],
    )

    print(f"OK -- R2 base={r2_base:.4f} -- importance momentum5j="
          f"{importance_momentum:.5f}, importance variation_vix={importance_vix:.5f} -- "
          f"{'VIX plus important' if importance_vix and importance_momentum and importance_vix > importance_momentum else 'momentum plus important ou comparable'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
