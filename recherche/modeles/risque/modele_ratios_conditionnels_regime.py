"""Modele -- Sharpe/Sortino conditionnels au regime de volatilite (VIX haut vs bas), pas des
ratios globaux comme modele_ratios_performance.py -- meme logique de conditionnement que
modele_var_conditionnelle_regime.py, appliquee aux ratios rendement/risque plutot qu'a la VaR.

Un Sharpe global peut masquer une realite tres differente selon le regime : rendement/risque
souvent MEILLEUR en regime calme (moins de risque pour un rendement similaire) que pendant les
episodes de stress -- verifie ici plutot que suppose.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, percentile_rang, read_series, rendements_log  # noqa: E402

NOM_MODELE = "ratios_conditionnels_regime"
SEUIL_VIX_HAUT_PERCENTILE = 66
JOURS_PAR_AN = 252


def sharpe(rendements: list) -> float:
    n = len(rendements)
    if n < 20:
        raise SerieVide("moins de 20 points")
    moyenne = sum(rendements) / n
    variance = sum((r - moyenne) ** 2 for r in rendements) / (n - 1)
    ecart_type = variance ** 0.5
    if ecart_type == 0:
        raise SerieVide("ecart-type nul")
    return (moyenne / ecart_type) * (JOURS_PAR_AN ** 0.5)


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
    vix_correspondant = niveaux_vix[1:]

    seuil_vix_split = sorted(niveaux_vix)[int(len(niveaux_vix) * SEUIL_VIX_HAUT_PERCENTILE / 100)]
    rendements_regime_haut = [r for r, v in zip(rendements_sp500, vix_correspondant)
                               if v >= seuil_vix_split]
    rendements_regime_bas = [r for r, v in zip(rendements_sp500, vix_correspondant)
                              if v < seuil_vix_split]

    try:
        sharpe_haut = sharpe(rendements_regime_haut)
        sharpe_bas = sharpe(rendements_regime_bas)
        sharpe_global = sharpe(rendements_sp500)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    date_du_jour = dates_communes[-1]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "sharpe_regime_haut_vol", "sharpe_regime_bas_vol", "sharpe_global"],
        [[date_du_jour, round(sharpe_haut, 3), round(sharpe_bas, 3), round(sharpe_global, 3)]],
    )

    print(f"OK -- Sharpe regime haut-vol={sharpe_haut:.3f}, bas-vol={sharpe_bas:.3f}, "
          f"global={sharpe_global:.3f} -- "
          f"{'meilleur en regime calme, comme attendu' if sharpe_bas > sharpe_haut else 'meilleur en regime de stress, contre-intuitif'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
