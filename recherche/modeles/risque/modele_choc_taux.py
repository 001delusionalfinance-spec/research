"""Modele -- sensibilite du S&P 500 a un choc de taux theorique (+/-100pb sur le 10 ans), via
le beta deja mesure (modele_beta_facteur_macro.py, statistique/).

Applique le beta glissant SP500/DGS10 a un choc hypothetique de +100pb et -100pb -- traduit un
coefficient de regression abstrait en un impact de prix concret. Pas une prevision (le beta
glissant peut changer), un scenario "si le regime actuel de sensibilite se maintenait".

**DFF (taux Fed funds) essaye en premier, abandonne en testant** : sur 90 jours, seulement 5
variations non nulles (bruit de 1pb autour du taux administre) -- extrapoler un beta instable
sur si peu de donnees a un choc de 100pb donnait un mouvement SP500 de +68,8%, absurde
economiquement. DGS10 (taux 10 ans, marche, variation quotidienne reelle) retenu a la place --
memes garde-fous que dans modele_beta_facteur_macro.py (minimum de variations non nulles exige
avant de calculer quoi que ce soit).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log  # noqa: E402

NOM_MODELE = "choc_taux"
FENETRE = 60
CHOC_PT = 1.0  # +/-100 points de base


def beta_regression(y: list, x: list) -> float:
    n = min(len(x), len(y))
    if n < 3:
        raise SerieVide("pas assez de points")
    x, y = x[-n:], y[-n:]
    mx, my = sum(x) / n, sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    var_x = sum((xi - mx) ** 2 for xi in x)
    if var_x == 0:
        raise SerieVide("variance nulle sur le facteur")
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
        print(f"echec -- seulement {n_variations_non_nulles}/{FENETRE} variations non nulles, "
              f"facteur trop plat")
        return 1

    try:
        beta = beta_regression(rendements_sp500[-FENETRE:], variations_dgs10[-FENETRE:])
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix_actuel = prix_sp500[-1]
    impact_hausse_pct = beta * CHOC_PT * 100
    impact_baisse_pct = beta * (-CHOC_PT) * 100
    niveau_apres_hausse = prix_actuel * (1 + impact_hausse_pct / 100)
    niveau_apres_baisse = prix_actuel * (1 + impact_baisse_pct / 100)

    date_du_jour = dates_communes[-1]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "beta_utilise", "prix_actuel", "impact_hausse_100pb_pct",
         "niveau_apres_hausse_taux", "impact_baisse_100pb_pct", "niveau_apres_baisse_taux"],
        [[date_du_jour, round(beta, 5), round(prix_actuel, 2), round(impact_hausse_pct, 2),
          round(niveau_apres_hausse, 1), round(impact_baisse_pct, 2),
          round(niveau_apres_baisse, 1)]],
    )

    print(f"OK -- beta SP500/DGS10={beta:.4f} -- choc +100pb : {impact_hausse_pct:+.2f}% "
          f"(SP500 {prix_actuel:.0f} -> {niveau_apres_hausse:.0f}) ; choc -100pb : "
          f"{impact_baisse_pct:+.2f}% (-> {niveau_apres_baisse:.0f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
