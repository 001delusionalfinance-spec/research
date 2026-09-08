"""Modele -- VAR(p) (Vector Autoregression) sur [rendement SP500, variation VIX] -- dynamique
CONJOINTE des deux series, chacune expliquee par ses propres lags ET les lags de l'autre.

Distinct de modele_causalite_granger.py (teste juste "est-ce que X ameliore la prevision de Y")
et modele_beta_vol.py (relation contemporaine, meme jour) : le VAR estime un systeme complet,
utilisable pour une prevision conjointe ou une fonction de reponse impulsionnelle. Ordre p
choisi par AIC (statsmodels le fait, pas fixe a la main).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log  # noqa: E402

NOM_MODELE = "var_sp500_vix"
MAX_LAGS = 10


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
    prix_sp500 = [map_sp500[d] for d in dates_communes]
    niveaux_vix = [map_vix[d] for d in dates_communes]

    rendements_sp500 = rendements_log(prix_sp500)
    variations_vix = [b - a for a, b in zip(niveaux_vix[:-1], niveaux_vix[1:])]
    date_du_jour = dates_communes[-1]

    import numpy as np
    from statsmodels.tsa.api import VAR

    donnees = np.column_stack([rendements_sp500, variations_vix])
    modele = VAR(donnees)
    ordre_choisi = modele.select_order(maxlags=MAX_LAGS).aic
    resultat = modele.fit(ordre_choisi if ordre_choisi > 0 else 1)

    # coefficient de l'effet "SP500 lag1 -> VIX" et "VIX lag1 -> SP500" -- lecture directe des
    # deux premiers coefficients (le lag le plus recent, generalement le plus interpretable).
    # params est un ndarray brut ici (entree numpy, pas pandas) -- verifie en testant, pas
    # suppose : .iloc n'existe pas sur un ndarray, seulement une indexation numpy standard.
    params = np.asarray(resultat.params)
    coef_sp500_vers_vix = float(params[1, 1]) if params.shape[0] > 1 else None
    coef_vix_vers_sp500 = float(params[1, 0]) if params.shape[0] > 1 else None

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "ordre_var_aic", "coef_sp500_vers_vix_lag1", "coef_vix_vers_sp500_lag1"],
        [[date_du_jour, ordre_choisi,
          round(coef_sp500_vers_vix, 5) if coef_sp500_vers_vix is not None else "",
          round(coef_vix_vers_sp500, 6) if coef_vix_vers_sp500 is not None else ""]],
    )

    if coef_sp500_vers_vix is not None:
        sens_sp500_vix = "SP500(t-1) en hausse -> VIX(t) tend a baisser (effet de levier)" \
            if coef_sp500_vers_vix < 0 else "SP500(t-1) en hausse -> VIX(t) tend aussi a monter"
    else:
        sens_sp500_vix = "non calculable"
    if coef_vix_vers_sp500 is not None:
        sens_vix_sp500 = "VIX(t-1) en hausse -> SP500(t) tend a baisser" \
            if coef_vix_vers_sp500 < 0 else "VIX(t-1) en hausse -> SP500(t) tend aussi a monter"
    else:
        sens_vix_sp500 = "non calculable"

    print(f"OK -- VAR ordre choisi par AIC={ordre_choisi} -- coef SP500(t-1)->VIX(t)="
          f"{coef_sp500_vers_vix} ({sens_sp500_vix}), coef VIX(t-1)->SP500(t)="
          f"{coef_vix_vers_sp500} ({sens_vix_sp500})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
