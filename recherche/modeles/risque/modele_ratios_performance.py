"""Modele -- Sharpe, Sortino, Calmar glissants (252j) du S&P 500 -- lecture de contexte, pas
un signal de trade (voir MAP.md : ce depot ne decide rien).

Trois ratios rendement/risque distincts, pas des synonymes : Sharpe divise par l'ecart-type
total (penalise la vol dans les deux sens) ; Sortino ne divise que par la vol des rendements
NEGATIFS (ne penalise pas la volatilite a la hausse, souvent juge plus juste) ; Calmar divise
par le drawdown maximal (parle a l'experience vecue d'une perte, pas a un ecart-type abstrait).
Taux sans risque suppose nul ici (simplification documentee -- DFF est disponible dans
donnees/brut/fred/ pour un futur raffinement, pas branche dans cette version).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs  # noqa: E402

NOM_MODELE = "ratios_performance"
FENETRE = 252
JOURS_PAR_AN = 252


def sharpe(rendements: list) -> float:
    n = len(rendements)
    if n < 20:
        raise SerieVide("moins de 20 points -- Sharpe non fiable")
    moyenne = sum(rendements) / n
    variance = sum((r - moyenne) ** 2 for r in rendements) / (n - 1)
    ecart_type = variance ** 0.5
    if ecart_type == 0:
        raise SerieVide("ecart-type nul -- Sharpe non defini")
    return (moyenne / ecart_type) * (JOURS_PAR_AN ** 0.5)


def sortino(rendements: list) -> float:
    n = len(rendements)
    if n < 20:
        raise SerieVide("moins de 20 points -- Sortino non fiable")
    moyenne = sum(rendements) / n
    negatifs = [r for r in rendements if r < 0]
    if len(negatifs) < 5:
        raise SerieVide("moins de 5 rendements negatifs -- vol a la baisse non fiable")
    vol_baisse = (sum(r ** 2 for r in negatifs) / len(negatifs)) ** 0.5
    if vol_baisse == 0:
        raise SerieVide("vol a la baisse nulle -- Sortino non defini")
    return (moyenne / vol_baisse) * (JOURS_PAR_AN ** 0.5)


def calmar(rendements: list, prix: list) -> float:
    if len(prix) < 2:
        raise SerieVide("pas assez de points pour un drawdown")
    plus_haut, pire = prix[0], 0.0
    for p in prix:
        plus_haut = max(plus_haut, p)
        pire = min(pire, (p - plus_haut) / plus_haut)
    if pire == 0:
        raise SerieVide("aucun drawdown observe -- Calmar non defini (division par zero)")
    rendement_annualise = sum(rendements) / len(rendements) * JOURS_PAR_AN
    return rendement_annualise / abs(pire)


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    date_du_jour = sp500[-1][0]
    fenetre_prix = prix[-FENETRE:]
    rendements = rendements_log(fenetre_prix)

    resultats = {}
    for nom, fonction in [("sharpe", lambda: sharpe(rendements)),
                           ("sortino", lambda: sortino(rendements)),
                           ("calmar", lambda: calmar(rendements, fenetre_prix))]:
        try:
            resultats[nom] = fonction()
        except SerieVide as e:
            print(f"{nom} : echec -- {e}")
            resultats[nom] = None

    if all(v is None for v in resultats.values()):
        print("echec -- aucun ratio calculable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "sharpe_252j", "sortino_252j", "calmar_252j"],
        [[date_du_jour] + [round(resultats[n], 4) if resultats[n] is not None else ""
                            for n in ["sharpe", "sortino", "calmar"]]],
    )

    print(f"OK -- Sharpe={resultats['sharpe']:.3f}, Sortino={resultats['sortino']:.3f}, "
          f"Calmar={resultats['calmar']:.3f} (taux sans risque suppose nul)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
