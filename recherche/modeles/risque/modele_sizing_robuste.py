"""Modele -- intervalle de confiance (bootstrap) sur l'estimation de volatilite realisee
S&P 500, pas juste un point.

Un chiffre de vol unique (ex. modele_var_drawdown.py, 11.8%) cache l'incertitude de son
ESTIMATION elle-meme -- sur un petit echantillon, l'intervalle peut etre large. Bootstrap
(rendements reechantillonnes avec remise, 1000 tirages, meme fenetre 252j que var_drawdown.py)
-- IC 90% [P5, P95] sur la vol annualisee resultante. Approche non parametrique (pas besoin de
supposer une distribution des rendements, coherent avec le choix deja fait pour VaR/CVaR
historiques).
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs, vol_annualisee  # noqa: E402

NOM_MODELE = "sizing_robuste"
FENETRE = 252
N_BOOTSTRAP = 1000
GRAINE = 42


def vol_depuis_rendements(rendements: list, jours_par_an: int = 252) -> float:
    """Meme formule que vol_annualisee (_lib.py), mais a partir de rendements deja calcules --
    le bootstrap reechantillonne les rendements eux-memes (i.i.d., l'ordre temporel n'a pas
    besoin d'etre preserve pour une estimation de variance), pas la peine de reconstruire un
    chemin de prix synthetique juste pour re-extraire des rendements identiques."""
    n = len(rendements)
    moyenne = sum(rendements) / n
    variance = sum((r - moyenne) ** 2 for r in rendements) / (n - 1)
    return (variance ** 0.5) * (jours_par_an ** 0.5)


def bootstrap_vol(rendements: list, n_tirages: int) -> list:
    rng = random.Random(GRAINE)
    n = len(rendements)
    resultats = []
    for _ in range(n_tirages):
        echantillon = [rendements[rng.randrange(n)] for _ in range(n)]
        resultats.append(vol_depuis_rendements(echantillon))
    return resultats


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    date_du_jour = sp500[-1][0]
    fenetre_prix = prix[-FENETRE - 1:]
    if len(fenetre_prix) < FENETRE // 2:
        print("echec -- historique insuffisant")
        return 1

    rendements = rendements_log(fenetre_prix)
    vol_point = vol_annualisee(fenetre_prix)

    resultats_bootstrap = bootstrap_vol(rendements, N_BOOTSTRAP)
    if len(resultats_bootstrap) < 100:
        print("echec -- bootstrap insuffisant")
        return 1

    resultats_tries = sorted(resultats_bootstrap)
    n = len(resultats_tries)
    p5 = resultats_tries[int(n * 0.05)]
    p95 = resultats_tries[int(n * 0.95)]

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "vol_point_estimate", "ic90_borne_basse", "ic90_borne_haute", "n_bootstrap"],
        [[date_du_jour, round(vol_point, 4), round(p5, 4), round(p95, 4), len(resultats_bootstrap)]],
    )

    # lecture qualitative -- largeur de l'IC90 relative au point estimate lui-meme : un
    # intervalle large par rapport au point estimate = incertitude elevee sur l'estimation,
    # un intervalle etroit = estimation relativement fiable
    largeur_ic = p95 - p5
    if vol_point:
        ratio_largeur = largeur_ic / vol_point
        if ratio_largeur >= 0.5:
            lecture_ic = f"intervalle large ({ratio_largeur*100:.0f}% du point estimate) -- incertitude elevee"
        elif ratio_largeur >= 0.25:
            lecture_ic = f"intervalle modere ({ratio_largeur*100:.0f}% du point estimate)"
        else:
            lecture_ic = f"intervalle etroit ({ratio_largeur*100:.0f}% du point estimate) -- estimation relativement fiable"
    else:
        lecture_ic = "point estimate nul -- ratio non calculable"

    print(f"OK -- vol point estimate={vol_point:.4f}, IC90%=[{p5:.4f}, {p95:.4f}] "
          f"({len(resultats_bootstrap)} tirages bootstrap) -- {lecture_ic}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
