"""Modele -- beta glissant du S&P 500 contre un facteur macro (variation du taux 10 ans US),
distinct de modele_beta_vol.py (beta contre le VIX, un facteur de marche, pas macro).

**DFF (taux Fed funds effectif) essaye puis abandonne en testant, pas suppose fonctionner** :
sur une fenetre de 90 jours, DFF n'a que ~5 variations non nulles, toutes de 1 point de base
(bruit de marche autour du taux administre, pas de vraies decisions Fed) -- une regression sur
un facteur quasi constant donne un beta instable, domine par une poignee de points de levier.
Beta mesure = 0.6882, extrapole a un choc de 100pb donnait un mouvement SP500 de +68,8% --
absurde economiquement, signal clair d'un facteur mal choisi, pas d'un vrai beta. DGS10 (taux
10 ans, marche, bouge en continu chaque jour) est le facteur retenu a la place -- bien plus
riche en variation exploitable pour une regression glissante.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log  # noqa: E402

NOM_MODELE = "beta_facteur_macro"
FENETRE = 60


def beta_regression(y: list, x: list) -> float:
    n = min(len(x), len(y))
    if n < 3:
        raise SerieVide("pas assez de points")
    x, y = x[-n:], y[-n:]
    mx, my = sum(x) / n, sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    var_x = sum((xi - mx) ** 2 for xi in x)
    if var_x == 0:
        raise SerieVide("variance nulle sur le facteur -- pas de mouvement de taux sur la "
                         "fenetre, beta non defini")
    return cov / var_x


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        dgs10 = read_series(BRUT / "fred" / "DGS10.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in sp500) & set(d for d, _ in dgs10))
    if len(dates_communes) < FENETRE + 1:
        print("echec -- pas assez de dates communes")
        return 1

    map_sp500, map_dgs10 = dict(sp500), dict(dgs10)
    prix_sp500 = [map_sp500[d] for d in dates_communes]
    niveaux_dgs10 = [map_dgs10[d] for d in dates_communes]

    rendements_sp500 = rendements_log(prix_sp500)
    variations_dgs10 = [b - a for a, b in zip(niveaux_dgs10[:-1], niveaux_dgs10[1:])]

    n_variations_non_nulles = sum(1 for v in variations_dgs10[-FENETRE:] if abs(v) > 1e-9)
    if n_variations_non_nulles < FENETRE // 2:
        print(f"echec -- seulement {n_variations_non_nulles}/{FENETRE} variations non nulles "
              f"sur la fenetre, facteur trop plat pour une regression fiable")
        return 1

    try:
        beta = beta_regression(rendements_sp500[-FENETRE:], variations_dgs10[-FENETRE:])
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    date_du_jour = dates_communes[-1]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "beta_sp500_dgs10_60j", "n_variations_non_nulles"],
        [[date_du_jour, round(beta, 5), n_variations_non_nulles]],
    )

    # Meme lecture que celle qui a fait rejeter DFF plus haut (docstring) : extrapoler le beta a
    # un choc de +100pb (1 point, l'unite de `beta` ici) donne un ordre de grandeur du mouvement
    # SP500 implique -- sert a juger si la sensibilite mesuree est plausible ou pas, pas juste
    # a afficher un chiffre brut.
    choc_100pb = math.exp(beta) - 1
    if abs(choc_100pb) >= 0.20:
        lecture = ("sensibilite tres elevee -- mouvement extrapole invraisemblable pour un choc "
                   "de taux, a interpreter avec prudence (meme type de signal que le rejet de "
                   "DFF ci-dessus)")
    elif abs(choc_100pb) >= 0.05:
        lecture = "sensibilite elevee au facteur macro"
    elif abs(choc_100pb) >= 0.01:
        lecture = "sensibilite normale au facteur macro"
    else:
        lecture = "sensibilite faible -- quasi insensible au facteur sur cette fenetre"

    print(f"OK -- beta SP500/DGS10 ({FENETRE}j) = {beta:.4f} (rendement SP500 pour +1pt de "
          f"taux 10 ans, {n_variations_non_nulles}/{FENETRE} jours avec variation reelle) -- "
          f"{lecture} (choc de +100pb extrapole = {choc_100pb:+.1%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
