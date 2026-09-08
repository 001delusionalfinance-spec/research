"""Modele -- facteur "qualite" applique au regime macro (pas a une action individuelle,
faute de fondamentaux d'entreprise ingeres) : stabilite recente du taux directeur et du VIX
comme proxy de previsibilite du regime actuel.

Un bloc dont le taux est stable ET dont le VIX est stable (faible ecart-type des variations
recentes) offre un environnement "de qualite" au sens ou l'incertitude court terme est faible --
distinct de "conditions accommodantes/restrictives" (deja mesure par modele_conditions_
financieres.py) : ici, la STABILITE compte, pas le niveau.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "qualite_regime_macro"
FENETRE = 60


def volatilite_relative(serie: list) -> float:
    """Ecart-type des variations, normalise par le niveau moyen -- coefficient de variation
    des variations, comparable entre des series d'echelles differentes (taux en % vs VIX en
    points)."""
    if len(serie) < 10:
        raise SerieVide("pas assez de points")
    variations = [b - a for a, b in zip(serie[:-1], serie[1:])]
    moyenne_niveau = sum(serie) / len(serie)
    if moyenne_niveau == 0:
        raise SerieVide("niveau moyen nul -- normalisation impossible")
    ecart_type_variations = (sum((v - sum(variations) / len(variations)) ** 2
                                   for v in variations) / len(variations)) ** 0.5
    return ecart_type_variations / abs(moyenne_niveau)


def main() -> int:
    try:
        dff = read_series(BRUT / "fred" / "DFF.csv")
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    try:
        instabilite_taux = volatilite_relative(valeurs(dff)[-FENETRE:])
        instabilite_vix = volatilite_relative(valeurs(vix)[-FENETRE:])
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    score_qualite = -(instabilite_taux + instabilite_vix) / 2  # negatif = moins d'instabilite
                                                                  # = "qualite" plus haute
    date_du_jour = dff[-1][0]

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "instabilite_taux", "instabilite_vix", "score_qualite_regime"],
        [[date_du_jour, round(instabilite_taux, 5), round(instabilite_vix, 5),
          round(score_qualite, 5)]],
    )

    print(f"OK -- instabilite taux={instabilite_taux:.4f}, instabilite VIX={instabilite_vix:.4f} "
          f"-- score qualite du regime={score_qualite:+.4f} (plus haut = regime plus stable/"
          f"previsible)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
