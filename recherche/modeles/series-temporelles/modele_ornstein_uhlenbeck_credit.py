"""Modele -- retour a la moyenne (Ornstein-Uhlenbeck) sur le spread de credit high-yield
(BAMLH0A0HYM2) -- meme technique que modele_ornstein_uhlenbeck_vix.py (VIX), nouvelle
application : le spread de credit a aussi un comportement mean-reverting documente
(contrairement au prix des actions, cf. Hurst SP500), mais avec une demi-vie generalement
plus longue (le credit reagit et se normalise plus lentement que la vol implicite).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "ornstein_uhlenbeck_credit"


def estimer_ou(serie: list) -> tuple:
    if len(serie) < 30:
        raise SerieVide("moins de 30 points -- estimation OU non fiable")
    x_avant = serie[:-1]
    variations = [b - a for a, b in zip(serie[:-1], serie[1:])]

    n = len(x_avant)
    moyenne_x = sum(x_avant) / n
    moyenne_var = sum(variations) / n
    cov = sum((x - moyenne_x) * (v - moyenne_var) for x, v in zip(x_avant, variations))
    var_x = sum((x - moyenne_x) ** 2 for x in x_avant)
    if var_x == 0:
        raise SerieVide("variance nulle")

    pente = cov / var_x
    theta = -pente
    intercept = moyenne_var - pente * moyenne_x
    if theta <= 0:
        raise SerieVide(f"theta estime <= 0 ({theta:.4f}) -- pas de retour a la moyenne "
                         f"detecte sur cette fenetre")
    mu = intercept / theta
    import math
    demi_vie = math.log(2) / theta
    return theta, mu, demi_vie


def main() -> int:
    try:
        hy = read_series(BRUT / "fred" / "BAMLH0A0HYM2.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    date_du_jour = hy[-1][0]
    try:
        theta, mu, demi_vie = estimer_ou(valeurs(hy))
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    spread_actuel = hy[-1][1]
    ecart_a_la_moyenne = spread_actuel - mu

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "spread_hy_actuel", "mu_niveau_moyen", "theta", "demi_vie_jours",
         "ecart_a_la_moyenne"],
        [[date_du_jour, spread_actuel, round(mu, 3), round(theta, 6), round(demi_vie, 1),
          round(ecart_a_la_moyenne, 3)]],
    )

    if ecart_a_la_moyenne > 0:
        lecture_niveau = "spread HY actuel au-dessus de son niveau moyen de long terme"
    elif ecart_a_la_moyenne < 0:
        lecture_niveau = "spread HY actuel en-dessous de son niveau moyen de long terme"
    else:
        lecture_niveau = "spread HY actuel exactement a son niveau moyen de long terme"

    print(f"OK -- spread HY actuel={spread_actuel:.2f}, niveau moyen estime={mu:.2f}, "
          f"demi-vie={demi_vie:.1f}j, ecart actuel={ecart_a_la_moyenne:+.2f} -- {lecture_niveau}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
