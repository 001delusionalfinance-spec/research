"""Modele -- test de stationnarite (Augmented Dickey-Fuller) sur les 5 taux directeurs.

Garde-fou methodologique manquant jusqu'ici : la plupart des techniques statistiques standard
(correlation de Pearson, regression) supposent implicitement des series stationnaires -- une
serie non-stationnaire (ex. un taux qui tend structurellement a la baisse depuis 40 ans) peut
produire des correlations "significatives" qui ne sont que deux tendances qui se croisent, pas
une vraie relation (biais classique de regression fallacieuse, Granger & Newbold 1974).

H0 du test ADF : la serie a une racine unitaire (non-stationnaire). p < 0,05 rejette H0 (donc
stationnaire). Utilise statsmodels (implementation de reference, pas reimplementee a la main --
contrairement a correlation_avec_p_valeur dans _lib.py qui est simple assez pour etre fiable
a la main, ADF ne l'est pas).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "stationnarite_taux"

SERIES = {
    "US": "DFF",
    "Zone_euro": "ECBDFR",
    "Royaume-Uni": "IUDSOIA",
    "Japon": "IRSTCI01JPM156N",
    "Chine": "IR3TIB01CNM156N",
}


def test_adf(valeurs_serie: list) -> tuple:
    from statsmodels.tsa.stattools import adfuller
    if len(valeurs_serie) < 20:
        raise SerieVide("moins de 20 points -- ADF non fiable")
    stat, p_valeur, *_ = adfuller(valeurs_serie, autolag="AIC")
    return stat, p_valeur


def main() -> int:
    resultats = []
    echecs = []
    date_du_jour = None
    for bloc, series_id in SERIES.items():
        try:
            serie = read_series(BRUT / "fred" / f"{series_id}.csv")
            date_du_jour = date_du_jour or serie[-1][0]
            stat, p_valeur = test_adf(valeurs(serie))
        except SerieVide as e:
            echecs.append((bloc, str(e)))
            print(f"{bloc} : echec -- {e}")
            continue
        stationnaire = p_valeur < 0.05
        resultats.append([date_du_jour, bloc, series_id, round(stat, 4), round(p_valeur, 4),
                           stationnaire])
        print(f"{bloc} ({series_id}) : ADF stat={stat:.3f}, p={p_valeur:.4f} -- "
              f"{'stationnaire' if stationnaire else 'NON-stationnaire'}")

    if not resultats:
        print("echec -- aucun bloc exploitable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "bloc", "serie", "adf_stat", "p_valeur", "stationnaire"],
        resultats,
    )

    n_stationnaires = sum(1 for r in resultats if r[5])
    print(f"\n{n_stationnaires}/{len(resultats)} series stationnaires (niveau, pas en "
          f"difference) -- a garder en tete avant toute correlation/regression sur ces series "
          f"telles quelles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
