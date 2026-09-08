"""Modele -- risque de queue (VaR/CVaR historique) et drawdown maximal, S&P 500.

VaR historique (pas parametrique -- ne suppose pas une distribution normale des rendements,
connue pour sous-estimer le risque de queue reel) : le rendement au rang correspondant au
seuil, sur une fenetre glissante de 252 jours (~1 an de bourse). CVaR (Expected Shortfall) :
moyenne des rendements pires que la VaR -- capture combien c'est grave au-dela du seuil, pas
seulement le seuil lui-meme.

Drawdown maximal : sur la MEME fenetre 252j, calcule sur l'indice de prix (pas sur les
rendements cumules artificiellement recomposes) -- evite un biais classique si les rendements
utilises pour la VaR et le prix brut divergeaient legerement (arrondis, jours manquants).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs  # noqa: E402

NOM_MODELE = "var_drawdown"
FENETRE_JOURS = 252
SEUILS = [0.95, 0.99]


def var_historique(rendements: list, seuil: float) -> float:
    """VaR historique au seuil donne (ex. 0.95 -> perte non depassee 95% du temps) --
    convention : retourne une valeur negative (une perte), pas une valeur absolue."""
    if len(rendements) < 20:
        raise SerieVide("moins de 20 rendements -- VaR non fiable sur un si petit echantillon")
    r_tries = sorted(rendements)
    rang = int((1 - seuil) * len(r_tries))
    return r_tries[max(0, rang)]


def cvar_historique(rendements: list, seuil: float) -> float:
    """Expected Shortfall -- moyenne des rendements pires que la VaR au meme seuil."""
    var = var_historique(rendements, seuil)
    pires = [r for r in rendements if r <= var]
    if not pires:
        raise SerieVide("aucun rendement au-dela de la VaR -- echantillon degenere")
    return sum(pires) / len(pires)


def drawdown_maximal(prix: list) -> float:
    """Plus grande chute depuis un plus haut glissant, sur la fenetre donnee -- valeur
    negative (ex. -0.15 = -15%)."""
    if len(prix) < 2:
        raise SerieVide("pas assez de points pour un drawdown")
    plus_haut = prix[0]
    pire = 0.0
    for p in prix:
        plus_haut = max(plus_haut, p)
        pire = min(pire, (p - plus_haut) / plus_haut)
    return pire


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    date_du_jour = sp500[-1][0]

    fenetre_prix = prix[-FENETRE_JOURS:]
    rendements_fenetre = rendements_log(fenetre_prix)

    resultats = {}
    for seuil in SEUILS:
        try:
            resultats[f"var_{int(seuil * 100)}"] = var_historique(rendements_fenetre, seuil)
            resultats[f"cvar_{int(seuil * 100)}"] = cvar_historique(rendements_fenetre, seuil)
        except SerieVide as e:
            print(f"seuil {seuil} : echec -- {e}")
            resultats[f"var_{int(seuil * 100)}"] = None
            resultats[f"cvar_{int(seuil * 100)}"] = None

    try:
        dd = drawdown_maximal(fenetre_prix)
    except SerieVide as e:
        print(f"drawdown : echec -- {e}")
        dd = None

    if all(v is None for v in list(resultats.values()) + [dd]):
        print("echec -- rien de calculable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "var_95_pct", "cvar_95_pct", "var_99_pct", "cvar_99_pct",
         "drawdown_max_252j_pct"],
        [[date_du_jour,
          round(resultats["var_95"] * 100, 3) if resultats["var_95"] is not None else "",
          round(resultats["cvar_95"] * 100, 3) if resultats["cvar_95"] is not None else "",
          round(resultats["var_99"] * 100, 3) if resultats["var_99"] is not None else "",
          round(resultats["cvar_99"] * 100, 3) if resultats["cvar_99"] is not None else "",
          round(dd * 100, 3) if dd is not None else ""]],
    )

    print(f"OK -- VaR95={resultats['var_95']*100:.2f}% CVaR95={resultats['cvar_95']*100:.2f}% "
          f"VaR99={resultats['var_99']*100:.2f}% CVaR99={resultats['cvar_99']*100:.2f}% "
          f"drawdown_max_252j={dd*100:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
