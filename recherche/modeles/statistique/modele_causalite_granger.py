"""Modele -- causalite de Granger entre variation du VIX et rendement S&P 500 (les deux sens
testes).

"Causalite" au sens de Granger = est-ce que les valeurs passees de X ameliorent la prevision de
Y au-dela des valeurs passees de Y seules -- pas une causalite structurelle/economique prouvee,
juste un ordre temporel predictif (Granger 1969, distinction que le nom du test induit souvent
en erreur, precisee ici explicitement). Test via statsmodels, 5 lags (une semaine de bourse).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log  # noqa: E402

NOM_MODELE = "causalite_granger"
LAGS = 5


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in sp500) & set(d for d, _ in vix))
    if len(dates_communes) < 100:
        print("echec -- pas assez de dates communes")
        return 1

    map_sp500, map_vix = dict(sp500), dict(vix)
    prix_sp500 = [map_sp500[d] for d in dates_communes]
    niveaux_vix = [map_vix[d] for d in dates_communes]

    rendements_sp500 = rendements_log(prix_sp500)
    variations_vix = [b - a for a, b in zip(niveaux_vix[:-1], niveaux_vix[1:])]
    date_du_jour = dates_communes[-1]

    import numpy as np
    from statsmodels.tsa.stattools import grangercausalitytests

    donnees_vix_cause_sp500 = np.column_stack([rendements_sp500, variations_vix])
    donnees_sp500_cause_vix = np.column_stack([variations_vix, rendements_sp500])

    resultats = {}
    for nom, donnees in [("VIX_cause_SP500", donnees_vix_cause_sp500),
                          ("SP500_cause_VIX", donnees_sp500_cause_vix)]:
        try:
            res = grangercausalitytests(donnees, maxlag=LAGS)
            p_valeur = res[LAGS][0]["ssr_ftest"][1]
            resultats[nom] = p_valeur
            causalite = p_valeur < 0.05
            sig = " *" if causalite else ""
            print(f"{nom} (lag={LAGS}) : p={p_valeur:.4f}{sig} -- "
                  f"{'causalite Granger detectee' if causalite else 'pas de causalite Granger detectee'}")
        except (ValueError, SerieVide) as e:
            print(f"{nom} : echec -- {e}")

    if not resultats:
        print("echec -- aucun test exploitable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "lags"] + list(resultats.keys()),
        [[date_du_jour, LAGS] + [round(p, 5) for p in resultats.values()]],
    )

    sens_significatifs = [nom for nom, p in resultats.items() if p < 0.05]
    if sens_significatifs:
        print(f"OK -- causalite Granger detectee : {', '.join(sens_significatifs)} (lag={LAGS})")
    else:
        print(f"OK -- aucune causalite Granger detectee (lag={LAGS}, "
              f"{len(resultats)}/2 sens testes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
