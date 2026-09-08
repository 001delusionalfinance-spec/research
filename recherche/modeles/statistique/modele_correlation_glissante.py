"""Modele -- correlation glissante S&P 500 / VIX, fenetre 60j.

Complete correlations_positionnement.py (un point fige dans le temps) avec la dimension qui
manque : COMMENT la relation evolue. La correlation SP500/VIX est structurellement negative
(la vol monte quand les actions baissent) mais son INTENSITE varie -- utile de voir si elle se
renforce ou se relache, pas seulement sa valeur actuelle.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import (BRUT, ETAT, SerieVide, accumuler_csv, correlation,  # noqa: E402
                   nouvelle_figure, read_series, rendements_log, sauvegarder_figure, valeurs)

NOM_MODELE = "correlation_glissante"
FENETRE = 60


def correlation_glissante(a: list, b: list, fenetre: int) -> list:
    """Liste de correlations, une par point a partir du (fenetre)-eme -- sur les RENDEMENTS,
    pas les niveaux (correlation de niveaux = biais classique, cf. modele_stationnarite_taux)."""
    n = min(len(a), len(b))
    if n < fenetre + 1:
        raise SerieVide(f"moins de {fenetre + 1} points communs pour une correlation glissante")
    out = []
    for i in range(fenetre, n):
        try:
            out.append(correlation(a[i - fenetre:i], b[i - fenetre:i]))
        except SerieVide:
            out.append(None)
    return out


def tracer(dates: list, correlations: list) -> None:
    plt, fig, ax = nouvelle_figure()
    ax.plot(dates, correlations, color="black", linewidth=1.2)
    ax.axhline(0, color="#bbbbbb", linewidth=0.8)
    ax.set_ylabel(f"Correlation glissante {FENETRE}j (rendements)")
    ax.set_xticks(ax.get_xticks()[::max(1, len(ax.get_xticks()) // 8)])
    ax.tick_params(axis="x", rotation=45)
    ax.set_title("Correlation glissante S&P 500 / VIX")
    sauvegarder_figure(plt, fig, NOM_MODELE, "correlation_glissante_sp500_vix")


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in sp500) & set(d for d, _ in vix))
    if len(dates_communes) < FENETRE + 1:
        print("echec -- pas assez de dates communes SP500/VIX")
        return 1

    map_sp500 = dict(sp500)
    map_vix = dict(vix)
    prix_sp500 = [map_sp500[d] for d in dates_communes]
    prix_vix = [map_vix[d] for d in dates_communes]

    rendements_sp500 = rendements_log(prix_sp500)
    rendements_vix = rendements_log(prix_vix)
    dates_rendements = dates_communes[1:]

    try:
        correlations = correlation_glissante(rendements_sp500, rendements_vix, FENETRE)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_correlations = dates_rendements[FENETRE:]
    correlations_valides = [c for c in correlations if c is not None]
    if not correlations_valides:
        print("echec -- aucune correlation calculable")
        return 1

    derniere_correlation = correlations[-1]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "correlation_60j_sp500_vix"],
        [[dates_correlations[-1], round(derniere_correlation, 4)
          if derniere_correlation is not None else ""]],
    )

    if len([c for c in correlations if c is not None]) >= 2:
        tracer(dates_correlations, correlations)

    print(f"OK -- correlation glissante {FENETRE}j SP500/VIX = {derniere_correlation:+.3f} "
          f"(min={min(correlations_valides):+.3f}, max={max(correlations_valides):+.3f} sur "
          f"la fenetre d'historique disponible)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
