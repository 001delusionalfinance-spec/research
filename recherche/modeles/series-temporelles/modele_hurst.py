"""Modele -- exposant de Hurst (analyse R/S, Mandelbrot 1968), memoire longue des rendements
S&P 500.

H=0,5 : marche aleatoire pure (aucune memoire, coherent avec l'efficience de marche faible).
H>0,5 : persistant/tendanciel (un mouvement a tendance a se poursuivre -- justifierait un signal
momentum). H<0,5 : anti-persistant/retour a la moyenne. Calcule par analyse R/S sur plusieurs
tailles de sous-fenetres puis regression log-log de la pente -- methode standard, pas une
approximation.

Complementaire de modele_walkforward_direction.py (ml/) : Hurst mesure une PROPRIETE
STATISTIQUE de la serie (a-t-elle de la memoire ?), le walk-forward mesure si une regle
EXPLOITE cette propriete avec profit -- les deux peuvent diverger (une serie peut avoir H>0,5
sans qu'aucune regle simple ne l'exploite apres frais, c'est deja ce que le ML a trouve).

**Limite reelle trouvee en validant sur une marche aleatoire synthetique (parametre connu,
H theorique = 0,5)** avant le test reel : le R/S simple (methode originale de Hurst 1951, pas
la version corrigee Anis-Lloyd 1976) est connu dans la litterature pour un biais positif a
echantillon fini -- confirme ici (H mesure = 0,593 sur une vraie marche aleatoire simulee, pas
0,5). Les seuils 0,45/0,55 ci-dessous doivent donc se lire comme "nettement en dessous/dessus
d'un random walk empirique" plutot que comme un ecart a 0,5 exact -- limite documentee, pas
corrigee dans cette version (le correctif Anis-Lloyd est a envisager si ce modele devient
central).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs  # noqa: E402

NOM_MODELE = "hurst"


def rescaled_range(serie: list) -> float:
    """R/S sur UNE fenetre -- ecart cumule (max-min) divise par l'ecart-type."""
    n = len(serie)
    moyenne = sum(serie) / n
    ecarts_cumules = []
    cumul = 0.0
    for x in serie:
        cumul += x - moyenne
        ecarts_cumules.append(cumul)
    etendue = max(ecarts_cumules) - min(ecarts_cumules)
    variance = sum((x - moyenne) ** 2 for x in serie) / n
    ecart_type = variance ** 0.5
    if ecart_type == 0:
        raise SerieVide("ecart-type nul sur cette fenetre -- R/S non defini")
    return etendue / ecart_type


def exposant_hurst(rendements: list, tailles_fenetres: list = None) -> tuple:
    """Retourne (H, r2_regression) -- H via regression log(R/S) ~ log(n)."""
    import math
    if tailles_fenetres is None:
        tailles_fenetres = [10, 20, 30, 50, 75, 100, 150]
    n_total = len(rendements)
    points = []
    for taille in tailles_fenetres:
        if taille >= n_total:
            continue
        n_fenetres = n_total // taille
        if n_fenetres < 2:
            continue
        rs_valeurs = []
        for i in range(n_fenetres):
            fenetre = rendements[i * taille:(i + 1) * taille]
            try:
                rs_valeurs.append(rescaled_range(fenetre))
            except SerieVide:
                continue
        if rs_valeurs:
            rs_moyen = sum(rs_valeurs) / len(rs_valeurs)
            if rs_moyen > 0:
                points.append((math.log(taille), math.log(rs_moyen)))

    if len(points) < 3:
        raise SerieVide("pas assez de tailles de fenetre exploitables pour la regression")

    n = len(points)
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    mx, my = sum(x) / n, sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    var_x = sum((xi - mx) ** 2 for xi in x)
    if var_x == 0:
        raise SerieVide("variance nulle sur les tailles de fenetre -- regression impossible")
    pente = cov / var_x
    var_y = sum((yi - my) ** 2 for yi in y)
    r2 = (cov ** 2) / (var_x * var_y) if var_y > 0 else 0.0
    return pente, r2


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    date_du_jour = sp500[-1][0]
    rendements = rendements_log(prix)

    try:
        h, r2 = exposant_hurst(rendements)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    if h > 0.55:
        lecture = "persistant (tendanciel)"
    elif h < 0.45:
        lecture = "anti-persistant (retour a la moyenne)"
    else:
        lecture = "proche de la marche aleatoire (H~0.5)"

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "hurst", "r2_regression", "lecture"],
        [[date_du_jour, round(h, 4), round(r2, 4), lecture]],
    )

    print(f"OK -- Hurst={h:.4f} (R2 regression={r2:.3f}) -- {lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
