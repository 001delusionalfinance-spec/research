"""Modele -- indice de conditions financieres US composite, simplifie (esprit Chicago Fed
NFCI, pas une reproduction exacte -- 3 composantes seulement, documentees).

Moyenne de 3 z-scores (chacun sur son propre historique disponible) : niveau du taux directeur
(DFF), spread de courbe (DGS10-DGS2, deja calcule par modele_courbe_taux_us.py, recalcule ici
independamment pour ne pas dependre de l'ordre d'execution des modeles), niveau du VIX. Un
indice positif = conditions plus restrictives que la moyenne historique (taux hauts, courbe
plate/inversee, vol elevee) ; negatif = plus accommodantes. Chaque composante deja utilisee
individuellement ailleurs (modele_taux_reel_us.py, modele_courbe_taux_us.py,
modele_volatilite_ewma.py) -- la valeur ajoutee ici est de les combiner en un seul chiffre.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "conditions_financieres"


def zscore_dernier_point(serie: list) -> float:
    if len(serie) < 20:
        raise SerieVide("moins de 20 points -- z-score non fiable")
    moyenne = sum(serie) / len(serie)
    variance = sum((v - moyenne) ** 2 for v in serie) / len(serie)
    ecart_type = variance ** 0.5
    if ecart_type == 0:
        raise SerieVide("ecart-type nul")
    return (serie[-1] - moyenne) / ecart_type


def main() -> int:
    try:
        dff = read_series(BRUT / "fred" / "DFF.csv")
        dgs10 = read_series(BRUT / "fred" / "DGS10.csv")
        dgs2 = read_series(BRUT / "fred" / "DGS2.csv")
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_courbe = sorted(set(d for d, _ in dgs10) & set(d for d, _ in dgs2))
    if not dates_courbe:
        print("echec -- aucune date commune DGS10/DGS2")
        return 1
    map10, map2 = dict(dgs10), dict(dgs2)
    spreads = [map10[d] - map2[d] for d in dates_courbe]
    spread_inverse = [-s for s in spreads]  # spread qui SE RETRECIT = plus restrictif -- on
                                              # inverse le signe pour que "plus haut" = "plus
                                              # restrictif" dans les 3 composantes, coherent

    composantes = {}
    echecs = []
    for nom, serie in [("taux_directeur", valeurs(dff)), ("courbe_inversee", spread_inverse),
                        ("vix", valeurs(vix))]:
        try:
            composantes[nom] = zscore_dernier_point(serie)
        except SerieVide as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")

    if len(composantes) < 2:
        print("echec -- moins de 2 composantes exploitables")
        return 1

    indice = sum(composantes.values()) / len(composantes)
    date_du_jour = dff[-1][0]

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "indice_composite", "n_composantes"] + list(composantes.keys()),
        [[date_du_jour, round(indice, 4), len(composantes)] +
         [round(v, 4) for v in composantes.values()]],
    )

    lecture = "restrictives" if indice > 0.5 else ("accommodantes" if indice < -0.5 else
                                                      "proches de la normale")
    print(f"OK -- indice conditions financieres={indice:+.3f} ({len(composantes)} composantes: "
          f"{composantes}) -- conditions {lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
