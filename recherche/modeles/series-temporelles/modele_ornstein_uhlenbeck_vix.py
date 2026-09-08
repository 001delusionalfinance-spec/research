"""Modele -- retour a la moyenne (Ornstein-Uhlenbeck) sur le VIX.

Le VIX est l'exemple manuel du processus mean-reverting en finance (contrairement au prix d'un
indice actions, qui se comporte plutot en marche aleatoire -- cf. modele_hurst.py, H~0.5-0.6
sur SP500). Version discrete : X_t - X_(t-1) = theta*(mu - X_(t-1)) + bruit -- regression
lineaire simple de la variation sur le niveau (pas besoin d'un solveur EDS, l'estimateur des
moindres carres de cette regression EST l'estimateur standard de theta/mu en temps discret,
Uhlenbeck & Ornstein 1930 / traitement econometrique classique).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "ornstein_uhlenbeck_vix"


def estimer_ou(serie: list) -> tuple:
    """Regression X_t - X_(t-1) = theta*(mu - X_(t-1)) + erreur -- retourne (theta, mu,
    demi_vie_jours)."""
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
        raise SerieVide("variance nulle sur le niveau -- regression impossible")

    pente = cov / var_x  # = -theta
    theta = -pente
    intercept = moyenne_var - pente * moyenne_x  # = theta * mu
    if theta <= 0:
        raise SerieVide(f"theta estime <= 0 ({theta:.4f}) -- pas de retour a la moyenne "
                         f"detecte sur cette fenetre, l'estimation OU ne s'applique pas")
    mu = intercept / theta
    import math
    demi_vie = math.log(2) / theta
    return theta, mu, demi_vie


def main() -> int:
    try:
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    date_du_jour = vix[-1][0]
    try:
        theta, mu, demi_vie = estimer_ou(valeurs(vix))
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    vix_actuel = vix[-1][1]
    ecart_a_la_moyenne = vix_actuel - mu

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "vix_actuel", "mu_niveau_moyen", "theta", "demi_vie_jours",
         "ecart_a_la_moyenne"],
        [[date_du_jour, vix_actuel, round(mu, 3), round(theta, 5), round(demi_vie, 1),
          round(ecart_a_la_moyenne, 3)]],
    )

    if ecart_a_la_moyenne > 0:
        lecture_niveau = "VIX actuel au-dessus de son niveau moyen de long terme"
    elif ecart_a_la_moyenne < 0:
        lecture_niveau = "VIX actuel en-dessous de son niveau moyen de long terme"
    else:
        lecture_niveau = "VIX actuel exactement a son niveau moyen de long terme"

    print(f"OK -- VIX actuel={vix_actuel:.2f}, niveau moyen estime (mu)={mu:.2f}, "
          f"demi-vie={demi_vie:.1f}j, ecart actuel={ecart_a_la_moyenne:+.2f} -- {lecture_niveau}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
