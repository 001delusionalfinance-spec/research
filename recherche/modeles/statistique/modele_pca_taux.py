"""Modele -- analyse en composantes principales (PCA) sur les 5 taux directeurs, aux dates
communes.

Technique standard pour une courbe de taux (Litterman-Scheinkman 1991, sur les maturites d'une
meme courbe -- adaptee ici aux 5 BLOCS plutot qu'aux maturites, meme logique : combien de
"facteurs" independants expliquent le mouvement conjoint). Une premiere composante qui explique
une tres grande part de la variance = les 5 banques centrales bougent largement ensemble (cycle
mondial synchronise) ; une premiere composante faible = mouvements largement independants par
bloc. Calcul direct (eigendecomposition de la matrice de covariance via numpy), pas sklearn --
2 a 5 dimensions, pas besoin d'une librairie ML pour ca.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "pca_taux"

SERIES = {
    "US": "DFF",
    "Zone_euro": "ECBDFR",
    "Royaume-Uni": "IUDSOIA",
    "Japon": "IRSTCI01JPM156N",
    "Chine": "IR3TIB01CNM156N",
}


def main() -> int:
    import numpy as np

    series_par_date = {}
    for bloc, series_id in SERIES.items():
        try:
            s = read_series(BRUT / "fred" / f"{series_id}.csv")
            series_par_date[bloc] = dict(s)
        except SerieVide as e:
            print(f"{bloc} : echec -- {e}")

    if len(series_par_date) < 2:
        print("echec -- moins de 2 blocs exploitables")
        return 1

    blocs = sorted(series_par_date.keys())
    dates_communes = sorted(set.intersection(*[set(series_par_date[b]) for b in blocs]))
    if len(dates_communes) < 20:
        print(f"echec -- seulement {len(dates_communes)} dates communes aux {len(blocs)} "
              f"blocs, moins de 20 -- PCA non fiable")
        return 1

    matrice = np.array([[series_par_date[b][d] for b in blocs] for d in dates_communes])
    matrice_centree = matrice - matrice.mean(axis=0)
    covariance = np.cov(matrice_centree, rowvar=False)

    valeurs_propres, vecteurs_propres = np.linalg.eigh(covariance)
    ordre = np.argsort(valeurs_propres)[::-1]  # decroissant
    valeurs_propres = valeurs_propres[ordre]
    vecteurs_propres = vecteurs_propres[:, ordre]

    variance_totale = valeurs_propres.sum()
    if variance_totale <= 0:
        print("echec -- variance totale nulle ou negative")
        return 1
    part_expliquee = valeurs_propres / variance_totale

    composante_1 = dict(zip(blocs, (float(v) for v in vecteurs_propres[:, 0].round(3))))
    date_du_jour = dates_communes[-1]

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_observations", "pct_variance_pc1", "pct_variance_pc2", "poids_pc1"],
        [[date_du_jour, len(dates_communes), round(part_expliquee[0] * 100, 2),
          round(part_expliquee[1] * 100, 2) if len(part_expliquee) > 1 else "",
          str(composante_1)]],
    )

    print(f"OK -- {len(dates_communes)} dates communes -- PC1 explique "
          f"{part_expliquee[0] * 100:.1f}% de la variance conjointe, poids PC1={composante_1}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
