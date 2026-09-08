"""Modele -- decomposition classique tendance/saisonnalite/residu (STL, Cleveland et al. 1990,
via statsmodels) sur le VIX -- complete modele_hp_filter_taux.py (HP, 2 composantes) et
modele_analyse_spectrale.py (FFT, cherche des periodes) avec une troisieme methode qui separe
EXPLICITEMENT une composante saisonniere (periode fixee) d'un residu, pas juste un spectre de
frequences.

Periode fixee a 5 (semaine de bourse) -- teste l'hypothese d'un effet jour-de-semaine, pas
suppose present.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "decomposition_stl"
PERIODE = 5


def main() -> int:
    try:
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    niveaux = valeurs(vix)
    date_du_jour = vix[-1][0]
    if len(niveaux) < 2 * PERIODE * 10:
        print("echec -- historique insuffisant pour une decomposition STL fiable")
        return 1

    from statsmodels.tsa.seasonal import STL

    resultat = STL(niveaux, period=PERIODE, robust=True).fit()

    variance_totale = sum((v - sum(niveaux) / len(niveaux)) ** 2 for v in niveaux)
    variance_saisonniere = sum((s - sum(resultat.seasonal) / len(resultat.seasonal)) ** 2
                                 for s in resultat.seasonal)
    part_saisonniere_pct = (variance_saisonniere / variance_totale * 100) if variance_totale > 0 \
        else 0

    tendance_actuelle = float(resultat.trend[-1])
    saisonnier_actuel = float(resultat.seasonal[-1])
    residu_actuel = float(resultat.resid[-1])

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "tendance", "composante_saisonniere", "residu", "part_variance_saisonniere_pct"],
        [[date_du_jour, round(tendance_actuelle, 3), round(saisonnier_actuel, 3),
          round(residu_actuel, 3), round(part_saisonniere_pct, 2)]],
    )

    print(f"OK -- VIX : tendance={tendance_actuelle:.2f}, composante saisonniere (periode "
          f"{PERIODE}j)={saisonnier_actuel:+.3f}, residu={residu_actuel:+.3f} -- la "
          f"saisonnalite explique {part_saisonniere_pct:.2f}% de la variance totale "
          f"({'negligeable' if part_saisonniere_pct < 1 else 'notable'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
