"""Modele -- detection d'anomalie multivariee (distance de Mahalanobis), rendement S&P 500 +
variation VIX conjoints.

Une anomalie univariee (juste un gros rendement SP500, ou juste un gros mouvement VIX) est deja
visible dans var_drawdown.py / positionnement_cot.py separement. L'interet ici est CONJOINT :
un jour peut etre anodin sur chaque dimension prise seule mais anormal dans leur COMBINAISON
(ex. SP500 qui monte fort ET VIX qui monte fort en meme temps -- rare, contraire a la relation
habituelle mesuree par modele_beta_vol.py). La distance de Mahalanobis mesure l'ecart a la
moyenne en tenant compte de la covariance entre les deux variables, pas juste chacune
isolement -- pas de sklearn (IsolationForest), calcul direct a la main (2 dimensions, matrice
2x2, inversion analytique -- pas besoin d'une librairie pour ca).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log  # noqa: E402

NOM_MODELE = "anomalie_multivariee"
FENETRE = 252
SEUIL_ANOMALIE = 3.0  # distance de Mahalanobis -- ~99.7e percentile en 2D sous hypothese
                        # gaussienne (a prendre avec la meme prudence que toute hypothese
                        # normale, cf. modele_skew_kurtosis.py qui montre des queues epaisses)


def mahalanobis_dernier_point(x: list, y: list) -> float:
    """Distance de Mahalanobis du dernier point (x[-1], y[-1]) au centre (moyenne) du nuage
    (x, y) -- matrice de covariance 2x2 inversee analytiquement."""
    n = len(x)
    if n < 20:
        raise SerieVide("moins de 20 points -- covariance non fiable")
    mx, my = sum(x) / n, sum(y) / n
    vxx = sum((xi - mx) ** 2 for xi in x) / (n - 1)
    vyy = sum((yi - my) ** 2 for yi in y) / (n - 1)
    vxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / (n - 1)

    det = vxx * vyy - vxy ** 2
    if abs(det) < 1e-12:
        raise SerieVide("matrice de covariance quasi singuliere -- Mahalanobis non fiable")

    # inverse d'une matrice 2x2 [[vxx, vxy], [vxy, vyy]]
    inv_xx, inv_yy, inv_xy = vyy / det, vxx / det, -vxy / det

    dx, dy = x[-1] - mx, y[-1] - my
    d2 = dx * dx * inv_xx + 2 * dx * dy * inv_xy + dy * dy * inv_yy
    if d2 < 0:
        raise SerieVide("distance au carre negative -- matrice non definie positive, bug reel "
                         "a corriger si ca arrive, pas une tolerance silencieuse")
    return d2 ** 0.5


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in sp500) & set(d for d, _ in vix))
    if len(dates_communes) < FENETRE + 1:
        print("echec -- pas assez de dates communes")
        return 1

    map_sp500, map_vix = dict(sp500), dict(vix)
    prix_sp500 = [map_sp500[d] for d in dates_communes]
    prix_vix = [map_vix[d] for d in dates_communes]

    rendements_sp500 = rendements_log(prix_sp500)
    variations_vix = [b - a for a, b in zip(prix_vix[:-1], prix_vix[1:])]

    fenetre_sp500 = rendements_sp500[-FENETRE:]
    fenetre_vix = variations_vix[-FENETRE:]

    try:
        distance = mahalanobis_dernier_point(fenetre_sp500, fenetre_vix)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    anomalie = distance > SEUIL_ANOMALIE
    date_du_jour = dates_communes[-1]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "rendement_sp500", "variation_vix", "distance_mahalanobis", "anomalie"],
        [[date_du_jour, round(fenetre_sp500[-1], 5), round(fenetre_vix[-1], 3),
          round(distance, 3), anomalie]],
    )

    print(f"OK -- distance de Mahalanobis={distance:.3f} (seuil {SEUIL_ANOMALIE}) -- "
          f"{'ANOMALIE conjointe' if anomalie else 'jour ordinaire'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
