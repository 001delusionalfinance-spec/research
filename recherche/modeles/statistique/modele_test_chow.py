"""Modele -- test de Chow (Chow 1960), rupture structurelle formelle sur la tendance du taux
10 ans US, entre les 6 premiers mois et les 6 derniers mois de l'historique disponible.

Distinct de modele_changepoint_volatilite.py : le changepoint CHERCHE le meilleur point de
coupure sans hypothese prealable (segmentation binaire), le test de Chow VERIFIE une coupure
PRECISEE A L'AVANCE (ici : le milieu de la fenetre 12 mois la plus recente) avec un vrai test F
et une p-valeur -- deux methodes complementaires, pas redondantes. H0 : le meme modele lineaire
(niveau + tendance temporelle) s'applique aux deux sous-periodes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "test_chow"
FENETRE_JOURS = 365


def ols_simple(y: list, x: list) -> tuple:
    """Retourne (intercept, pente, RSS) -- regression y ~ a + b*x."""
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    var_x = sum((xi - mx) ** 2 for xi in x)
    if var_x == 0:
        raise SerieVide("variance nulle sur x -- regression impossible")
    b = cov / var_x
    a = my - b * mx
    rss = sum((yi - (a + b * xi)) ** 2 for xi, yi in zip(x, y))
    return a, b, rss


def test_chow(y: list) -> tuple:
    """Coupe y en deux moities egales, teste si une seule regression lineaire (temps) explique
    aussi bien que deux regressions separees. Retourne (F_stat, p_valeur)."""
    from scipy import stats
    n = len(y)
    if n < 40:
        raise SerieVide("moins de 40 points -- test de Chow non fiable")
    milieu = n // 2
    x = list(range(n))
    x1, y1 = x[:milieu], y[:milieu]
    x2, y2 = x[milieu:], y[milieu:]

    _, _, rss_pool = ols_simple(y, x)
    _, _, rss1 = ols_simple(y1, x1)
    _, _, rss2 = ols_simple(y2, x2)

    k = 2  # intercept + pente
    ddl1 = k
    ddl2 = n - 2 * k
    if ddl2 <= 0:
        raise SerieVide("pas assez de degres de liberte")

    numerateur = (rss_pool - (rss1 + rss2)) / ddl1
    denominateur = (rss1 + rss2) / ddl2
    if denominateur <= 0:
        raise SerieVide("denominateur non positif")
    f_stat = numerateur / denominateur
    p_valeur = float(1 - stats.f.cdf(f_stat, ddl1, ddl2))
    return f_stat, p_valeur


def main() -> int:
    try:
        dgs10 = read_series(BRUT / "fred" / "DGS10.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    valeurs_recentes = [v for _, v in dgs10[-FENETRE_JOURS:]]
    date_du_jour = dgs10[-1][0]

    try:
        f_stat, p_valeur = test_chow(valeurs_recentes)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    rupture_significative = p_valeur < 0.05
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "f_stat", "p_valeur", "rupture_significative"],
        [[date_du_jour, round(f_stat, 3), round(p_valeur, 5), rupture_significative]],
    )

    print(f"OK -- test de Chow (taux 10 ans, 1ere vs 2eme moitie des 12 derniers mois) : "
          f"F={f_stat:.3f}, p={p_valeur:.4f} -- "
          f"{'RUPTURE structurelle significative' if rupture_significative else 'pas de rupture significative'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
