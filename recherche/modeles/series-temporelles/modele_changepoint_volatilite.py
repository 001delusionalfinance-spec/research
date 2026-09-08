"""Modele -- detection de rupture (changepoint) sur le niveau de volatilite du S&P 500.

Segmentation binaire a UN point de rupture (pas une methode multi-ruptures type PELT --
volontairement plus simple, teste sur cas synthetique avant le reel) : cherche l'indice qui
minimise la somme des carres intra-segment (equivalent a maximiser la separation
inter-segment) sur les rendements au carre (proxy de variance locale, pas les rendements bruts
-- une rupture de NIVEAU DE VOL est plus frequente et plus stable a detecter qu'une rupture de
rendement moyen sur des actions).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs  # noqa: E402

NOM_MODELE = "changepoint_volatilite"
MARGE_MIN_SEGMENT = 20  # eviter des segments trop courts pour etre fiables


def sse(valeurs_segment: list) -> float:
    if not valeurs_segment:
        return 0.0
    moyenne = sum(valeurs_segment) / len(valeurs_segment)
    return sum((v - moyenne) ** 2 for v in valeurs_segment)


def trouver_rupture(serie: list, marge: int = MARGE_MIN_SEGMENT) -> tuple:
    """Retourne (indice_rupture, sse_avant, sse_apres, reduction_relative)."""
    n = len(serie)
    if n < 2 * marge:
        raise SerieVide(f"moins de {2 * marge} points -- pas assez pour deux segments fiables")

    sse_total = sse(serie)
    if sse_total == 0:
        raise SerieVide("SSE total nul -- serie constante")

    meilleur_indice, meilleure_sse = None, float("inf")
    for i in range(marge, n - marge):
        s = sse(serie[:i]) + sse(serie[i:])
        if s < meilleure_sse:
            meilleure_sse, meilleur_indice = s, i

    reduction_relative = (sse_total - meilleure_sse) / sse_total
    return meilleur_indice, sse(serie[:meilleur_indice]), sse(serie[meilleur_indice:]), \
        reduction_relative


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    dates = [d for d, _ in sp500]
    rendements = rendements_log(prix)
    rendements_carres = [r ** 2 for r in rendements]

    try:
        indice, sse_avant, sse_apres, reduction = trouver_rupture(rendements_carres)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    date_rupture = dates[indice + 1]  # +1 car rendements[i] correspond a dates[i+1]
    vol_avant = (sum(rendements_carres[:indice]) / indice) ** 0.5 * (252 ** 0.5)
    vol_apres = (sum(rendements_carres[indice:]) / (len(rendements_carres) - indice)) ** 0.5 \
        * (252 ** 0.5)

    date_du_jour = dates[-1]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "date_rupture_detectee", "vol_annualisee_avant", "vol_annualisee_apres",
         "reduction_sse_relative"],
        [[date_du_jour, date_rupture, round(vol_avant, 4), round(vol_apres, 4),
          round(reduction, 4)]],
    )

    print(f"OK -- rupture detectee le {date_rupture} -- vol avant={vol_avant:.4f}, "
          f"vol apres={vol_apres:.4f} (reduction SSE={reduction:.1%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
