"""Modele -- scenario de choc de volatilite PARAMETRIQUE (VaR/CVaR recalculees sous une vol
choquee x2, x3) -- distinct de modele_stress_test_historique.py (rejoue un episode HISTORIQUE
reel) : ici, un choc HYPOTHETIQUE construit a partir de la distribution actuelle mise a
l'echelle, permet de tester des multiplicateurs qui n'ont pas d'equivalent historique exact
dans les 30 ans disponibles.

VaR parametrique gaussienne mise a l'echelle (pas historique comme var_drawdown.py) --
approche complementaire, pas un remplacement (repose sur l'hypothese normale, deja discutee
comme limitee ailleurs dans ce depot -- skew/kurtosis mesures separement, limite assumee ici
aussi).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs, vol_annualisee  # noqa: E402

NOM_MODELE = "choc_vol_parametrique"
FENETRE = 252
MULTIPLICATEURS = [1.0, 2.0, 3.0]
Z_95 = 1.645  # quantile gaussien 95%


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
    vol_actuelle_annuelle = vol_annualisee(fenetre_prix)
    vol_quotidienne = vol_actuelle_annuelle / (252 ** 0.5)
    moyenne_quotidienne = sum(rendements) / len(rendements)

    resultats = []
    for mult in MULTIPLICATEURS:
        vol_choquee = vol_quotidienne * mult
        var_parametrique = moyenne_quotidienne - Z_95 * vol_choquee
        resultats.append((mult, vol_choquee * (252 ** 0.5), var_parametrique))
        print(f"choc x{mult:.0f} : vol annualisee={vol_choquee * (252**0.5)*100:.1f}%, "
              f"VaR95 parametrique={var_parametrique*100:.2f}%/jour")

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "vol_actuelle_annualisee_pct"] +
        [f"var95_x{int(m)}_pct" for m in MULTIPLICATEURS],
        [[date_du_jour, round(vol_actuelle_annuelle * 100, 3)] +
         [round(r[2] * 100, 3) for r in resultats]],
    )

    print(f"OK -- vol actuelle={vol_actuelle_annuelle*100:.2f}%, scenarios x1/x2/x3 calcules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
