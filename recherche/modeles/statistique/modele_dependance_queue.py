"""Modele -- dependance de queue empirique (esprit copule) entre S&P 500 et VIX -- au-dela de
la correlation lineaire (deja mesuree par modele_correlation_glissante.py).

Question posee : quand le VIX est dans ses pires 10% de hausses, le SP500 est-il dans ses
pires 10% de baisses PLUS SOUVENT que ne le predirait l'independance (10% x 10% = 1% du temps
si independants) ? Coefficient de dependance de queue empirique = P(les deux dans leurs
10% extremes) / (10% x 10%) -- >1 = dependance de queue reelle (les evenements extremes des
deux series arrivent ensemble plus souvent que le hasard), proche de 1 = independance
approximative dans les queues, meme si la correlation globale est forte. Non-parametrique
(comptage direct, pas de copule parametrique ajustee -- plus simple, documente comme tel).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log  # noqa: E402

NOM_MODELE = "dependance_queue"
QUANTILE = 0.10


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in sp500) & set(d for d, _ in vix))
    if len(dates_communes) < 200:
        print("echec -- moins de 200 dates communes")
        return 1

    map_sp500, map_vix = dict(sp500), dict(vix)
    prix_sp500 = [map_sp500[d] for d in dates_communes]
    niveaux_vix = [map_vix[d] for d in dates_communes]

    rendements_sp500 = rendements_log(prix_sp500)
    variations_vix = [b - a for a, b in zip(niveaux_vix[:-1], niveaux_vix[1:])]
    date_du_jour = dates_communes[-1]

    n = len(rendements_sp500)
    seuil_sp500_bas = sorted(rendements_sp500)[int(n * QUANTILE)]
    seuil_vix_haut = sorted(variations_vix)[int(n * (1 - QUANTILE))]

    sp500_extreme = [r <= seuil_sp500_bas for r in rendements_sp500]
    vix_extreme = [v >= seuil_vix_haut for v in variations_vix]

    n_conjoint = sum(1 for a, b in zip(sp500_extreme, vix_extreme) if a and b)
    p_conjoint_observee = n_conjoint / n
    p_conjoint_independance = QUANTILE * QUANTILE
    coefficient_dependance = p_conjoint_observee / p_conjoint_independance \
        if p_conjoint_independance > 0 else None

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_observations", "n_jours_conjoints_extremes", "p_observee",
         "p_sous_independance", "coefficient_dependance_queue"],
        [[date_du_jour, n, n_conjoint, round(p_conjoint_observee, 5),
          round(p_conjoint_independance, 5),
          round(coefficient_dependance, 2) if coefficient_dependance else ""]],
    )

    print(f"OK -- {n_conjoint}/{n} jours conjointement extremes (SP500 pire {QUANTILE:.0%} ET "
          f"VIX pire {QUANTILE:.0%}), P observee={p_conjoint_observee:.4f} vs P sous "
          f"independance={p_conjoint_independance:.4f} -- coefficient de dependance de queue="
          f"{coefficient_dependance:.2f} ({'dependance reelle' if coefficient_dependance and coefficient_dependance > 1.5 else 'proche de l independance'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
