"""Modele -- cointegration (Engle-Granger) entre le S&P 500 et chacun de ses 10 secteurs --
extension de modele_cointegration_taux.py (taux) aux prix d'actifs.

Tous les secteurs sont des composantes du S&P 500 par construction, donc une forte cointegration
est attendue par defaut -- l'interessant est de reperer lequel s'en ECARTE (moins cointegre que
les autres, signe d'un decouplage structurel du secteur par rapport a l'indice large, pas juste
une divergence de rendement court terme deja visible dans modele_rotation_sectorielle.py).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "cointegration_secteurs"
SECTEURS = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE"]


def test_engle_granger(a: list, b: list) -> tuple:
    from statsmodels.tsa.stattools import coint
    n = min(len(a), len(b))
    if n < 30:
        raise SerieVide("moins de 30 points communs")
    stat, p_valeur, _ = coint(a[-n:], b[-n:])
    return stat, p_valeur


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    map_sp500 = dict(sp500)
    date_du_jour = sp500[-1][0]

    resultats = []
    for secteur in SECTEURS:
        try:
            serie_secteur = read_series(BRUT / "yfinance" / f"{secteur}.csv", value_col="close")
        except (SerieVide, FileNotFoundError) as e:
            print(f"{secteur} : echec -- {e}")
            continue
        dates_communes = sorted(set(map_sp500) & set(d for d, _ in serie_secteur))
        map_secteur = dict(serie_secteur)
        prix_sp500_aligne = [map_sp500[d] for d in dates_communes]
        prix_secteur_aligne = [map_secteur[d] for d in dates_communes]
        try:
            stat, p = test_engle_granger(prix_sp500_aligne, prix_secteur_aligne)
        except SerieVide as e:
            print(f"{secteur} : echec -- {e}")
            continue
        cointegres = p < 0.05
        resultats.append([date_du_jour, secteur, round(stat, 4), round(p, 4), cointegres])
        print(f"SP500/{secteur} : stat={stat:.3f}, p={p:.4f} -- "
              f"{'cointegres' if cointegres else 'NON cointegres'}")

    if not resultats:
        print("echec -- aucun secteur exploitable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "secteur", "stat_eg", "p_valeur", "cointegres"],
        resultats,
    )
    n_cointegres = sum(1 for r in resultats if r[4])
    non_cointegres = [r[1] for r in resultats if not r[4]]
    print(f"\n{n_cointegres}/{len(resultats)} secteurs cointegres avec SP500" +
          (f" -- decouples : {non_cointegres}" if non_cointegres else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
