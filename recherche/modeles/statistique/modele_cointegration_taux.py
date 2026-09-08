"""Modele -- cointegration (Engle-Granger) entre paires de taux directeurs.

Distinct de la correlation (correlations_positionnement.py) : deux series peuvent ne pas etre
correlees a court terme (rendements/variations) tout en partageant un equilibre de LONG TERME
(niveaux qui ne divergent jamais durablement) -- c'est ce que teste la cointegration, pas la
correlation. Test d'Engle-Granger (regression + test de racine unitaire sur les residus, via
statsmodels) -- methode standard, pas reimplementee a la main (contrairement a `correlation`
dans _lib.py, plus simple).

H0 : pas de cointegration. p < 0.05 rejette H0 (donc cointegrees).
"""

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "cointegration_taux"

SERIES = {
    "US": "DFF",
    "Zone_euro": "ECBDFR",
    "Royaume-Uni": "IUDSOIA",
    "Japon": "IRSTCI01JPM156N",
    "Chine": "IR3TIB01CNM156N",
}


def test_engle_granger(a: list, b: list) -> tuple:
    from statsmodels.tsa.stattools import coint
    n = min(len(a), len(b))
    if n < 30:
        raise SerieVide("moins de 30 points communs -- test non fiable")
    stat, p_valeur, _ = coint(a[-n:], b[-n:])
    return stat, p_valeur


def main() -> int:
    series_par_date = {}
    date_du_jour = None
    for bloc, series_id in SERIES.items():
        try:
            s = read_series(BRUT / "fred" / f"{series_id}.csv")
            date_du_jour = date_du_jour or s[-1][0]
            series_par_date[bloc] = dict(s)
        except SerieVide as e:
            print(f"{bloc} : echec -- {e}")

    if len(series_par_date) < 2:
        print("echec -- moins de 2 blocs exploitables")
        return 1

    resultats = []
    for bloc_a, bloc_b in itertools.combinations(sorted(series_par_date.keys()), 2):
        # alignement par date commune -- obligatoire avant tout test conjoint, les series
        # melangent frequence quotidienne et mensuelle (bug qu'une simple troncature "derniers
        # n points de chaque serie" aurait cache silencieusement -- dates non comparables)
        dates_communes = sorted(set(series_par_date[bloc_a]) & set(series_par_date[bloc_b]))
        a = [series_par_date[bloc_a][d] for d in dates_communes]
        b = [series_par_date[bloc_b][d] for d in dates_communes]
        try:
            stat, p = test_engle_granger(a, b)
        except SerieVide as e:
            print(f"{bloc_a}/{bloc_b} : echec -- {e}")
            continue
        cointegrees = p < 0.05
        resultats.append([date_du_jour, bloc_a, bloc_b, round(stat, 4), round(p, 4),
                           cointegrees])
        print(f"{bloc_a} / {bloc_b} : stat={stat:.3f}, p={p:.4f} -- "
              f"{'cointegrees' if cointegrees else 'non cointegrees'}")

    if not resultats:
        print("echec -- aucune paire testable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "bloc_a", "bloc_b", "stat_eg", "p_valeur", "cointegrees"],
        resultats,
    )
    n_cointegrees = sum(1 for r in resultats if r[5])
    print(f"\n{n_cointegrees}/{len(resultats)} paires cointegrees")
    return 0


if __name__ == "__main__":
    sys.exit(main())
