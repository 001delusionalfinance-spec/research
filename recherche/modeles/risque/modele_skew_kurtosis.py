"""Modele -- skewness et kurtosis (aplatissement) glissants des rendements S&P 500, fenetre
252j.

Complete var_drawdown.py : la VaR/CVaR resument la queue en un ou deux nombres, skew/kurtosis
decrivent la FORME de toute la distribution. Kurtosis en exces (> 0, convention Fisher --
normale = 0) = queues plus epaisses qu'une gaussienne, risque d'evenement extreme sous-estime
par toute methode qui suppose la normalite. Skew negatif = pertes extremes plus frequentes/
severes que les gains extremes -- fait stylise bien documente des rendements actions
(Cont 2001).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs  # noqa: E402

NOM_MODELE = "skew_kurtosis"
FENETRE = 252


def skewness(rendements: list) -> float:
    n = len(rendements)
    if n < 20:
        raise SerieVide("moins de 20 points -- skewness non fiable")
    moyenne = sum(rendements) / n
    m2 = sum((r - moyenne) ** 2 for r in rendements) / n
    m3 = sum((r - moyenne) ** 3 for r in rendements) / n
    if m2 == 0:
        raise SerieVide("variance nulle -- skewness non definie")
    return m3 / (m2 ** 1.5)


def kurtosis_exces(rendements: list) -> float:
    """Convention Fisher -- 0 pour une gaussienne (pas 3)."""
    n = len(rendements)
    if n < 20:
        raise SerieVide("moins de 20 points -- kurtosis non fiable")
    moyenne = sum(rendements) / n
    m2 = sum((r - moyenne) ** 2 for r in rendements) / n
    m4 = sum((r - moyenne) ** 4 for r in rendements) / n
    if m2 == 0:
        raise SerieVide("variance nulle -- kurtosis non definie")
    return m4 / (m2 ** 2) - 3


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    date_du_jour = sp500[-1][0]
    rendements = rendements_log(prix)
    fenetre_rendements = rendements[-FENETRE:]

    try:
        skew = skewness(fenetre_rendements)
        kurt = kurtosis_exces(fenetre_rendements)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "skewness_252j", "kurtosis_exces_252j"],
        [[date_du_jour, round(skew, 4), round(kurt, 4)]],
    )

    lecture_skew = "asymetrie negative (pertes extremes > gains extremes)" if skew < -0.1 else \
        ("asymetrie positive" if skew > 0.1 else "quasi symetrique")
    lecture_kurt = "queues epaisses (risque extreme sous-estime par une hypothese normale)" \
        if kurt > 0.5 else "proche d'une gaussienne"

    print(f"OK -- skewness={skew:+.3f} ({lecture_skew}), kurtosis exces={kurt:+.3f} "
          f"({lecture_kurt})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
