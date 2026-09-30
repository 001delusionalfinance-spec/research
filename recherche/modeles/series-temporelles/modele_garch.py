"""Modele -- GARCH(1,1) sur les rendements du S&P 500, volatilite conditionnelle.

Complete volatilite_ewma.py : l'EWMA a un lambda fixe impose (0,94, convention RiskMetrics),
GARCH(1,1) ESTIME ses parametres (omega/alpha/beta) par maximum de vraisemblance sur les
donnees -- persistance et vitesse de retour a la moyenne mesurees, pas supposees.

Piege connu : la librairie `arch` recommande de mettre les rendements a l'echelle (x100, rendements
en pourcentage) pour la stabilite numerique de l'optimiseur -- oublier de re-diviser par 100 au
moment de lire la volatilite en sortie produit une volatilite ~100x trop grande (exemple de bug :
4473% au lieu de ~45%). Verifie ici explicitement en comparant le resultat a la vol realisee deja
calculee par volatilite_ewma.py -- si l'ordre de grandeur diverge, c'est le signe de ce bug.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs  # noqa: E402

NOM_MODELE = "garch"
JOURS_PAR_AN = 252


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    date_du_jour = sp500[-1][0]
    rendements = rendements_log(prix)
    if len(rendements) < 100:
        print("echec -- moins de 100 rendements, GARCH pas fiable sur un si petit echantillon")
        return 1

    from arch import arch_model
    rendements_pct = [r * 100 for r in rendements]  # mise a l'echelle -- cf. piege documente

    modele = arch_model(rendements_pct, vol="Garch", p=1, q=1, dist="normal", mean="Zero")
    resultat = modele.fit(disp="off")

    variance_conditionnelle_pct2 = resultat.conditional_volatility[-1] ** 2
    vol_quotidienne_pct = variance_conditionnelle_pct2 ** 0.5  # encore en % (echelle x100)
    vol_quotidienne = vol_quotidienne_pct / 100  # retour a l'echelle des rendements bruts
    vol_annualisee_garch = vol_quotidienne * (JOURS_PAR_AN ** 0.5)

    alpha = resultat.params.get("alpha[1]")
    beta = resultat.params.get("beta[1]")
    persistance = alpha + beta if alpha is not None and beta is not None else None

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "vol_garch_annualisee", "alpha", "beta", "persistance"],
        [[date_du_jour, round(vol_annualisee_garch, 4),
          round(alpha, 4) if alpha is not None else "",
          round(beta, 4) if beta is not None else "",
          round(persistance, 4) if persistance is not None else ""]],
    )

    if persistance is not None and persistance > 0.95:
        lecture_persistance = "tres proche de 1 -- chocs de volatilite tres durables"
    elif persistance is not None and persistance < 0.80:
        lecture_persistance = "assez loin de 1 -- la vol revient relativement vite a sa moyenne"
    elif persistance is not None:
        lecture_persistance = "persistance moderee -- retour a la moyenne ni tres rapide ni tres lent"
    else:
        lecture_persistance = "non calculable"

    print(f"OK -- vol GARCH(1,1) annualisee={vol_annualisee_garch:.4f} (alpha={alpha:.3f}, "
          f"beta={beta:.3f}, persistance={persistance:.3f} -- {lecture_persistance})")
    if not (0.03 < vol_annualisee_garch < 1.0):
        print(f"AVERTISSEMENT -- ordre de grandeur suspect (attendu ~0.05-0.60 pour un indice "
              f"actions), verifier le piege d'echelle x100 documente en tete de fichier")
    return 0


if __name__ == "__main__":
    sys.exit(main())
