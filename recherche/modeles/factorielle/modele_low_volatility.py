"""Modele -- test du facteur "low volatility" (anomalie documentee : les actifs les moins
volatils ont historiquement un ratio rendement/risque MEILLEUR que les plus volatils, contraire
a l'intuition CAPM -- Ang, Hodrick, Xing & Zhang 2006, Baker/Bradley/Wurgler 2011), sur les 10
secteurs S&P 500.

Classe les secteurs par vol realisee (60j), compare le Sharpe du tercile le moins volatil au
tercile le plus volatil. Teste, pas affirme -- avec seulement 10 secteurs (donc ~3 par tercile),
la puissance statistique est faible, limite documentee.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs, vol_annualisee  # noqa: E402

NOM_MODELE = "low_volatility"
FENETRE_JOURS = 90

SECTEURS = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE"]


def sharpe_simple(rendements: list) -> float:
    n = len(rendements)
    moyenne = sum(rendements) / n
    variance = sum((r - moyenne) ** 2 for r in rendements) / (n - 1)
    ecart_type = variance ** 0.5
    if ecart_type == 0:
        raise SerieVide("ecart-type nul")
    return (moyenne / ecart_type) * (252 ** 0.5)


def main() -> int:
    resultats = {}
    date_du_jour = None
    for ticker in SECTEURS:
        try:
            serie = read_series(BRUT / "yfinance" / f"{ticker}.csv", value_col="close")
            date_du_jour = date_du_jour or serie[-1][0]
            prix = valeurs(serie)[-FENETRE_JOURS - 1:]
            rendements = rendements_log(prix)
            vol = vol_annualisee(prix)
            sharpe = sharpe_simple(rendements)
        except (SerieVide, FileNotFoundError) as e:
            print(f"{ticker} : echec -- {e}")
            continue
        resultats[ticker] = (vol, sharpe)

    if len(resultats) < 6:
        print("echec -- moins de 6 secteurs exploitables, terciles non pertinents")
        return 1

    classes = sorted(resultats.items(), key=lambda kv: kv[1][0])  # tri par vol croissante
    n = len(classes)
    taille_tercile = n // 3
    tercile_bas_vol = classes[:taille_tercile]
    tercile_haut_vol = classes[-taille_tercile:]

    sharpe_bas_vol = sum(s for _, (_, s) in tercile_bas_vol) / len(tercile_bas_vol)
    sharpe_haut_vol = sum(s for _, (_, s) in tercile_haut_vol) / len(tercile_haut_vol)
    anomalie_confirmee = sharpe_bas_vol > sharpe_haut_vol

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_secteurs", "secteurs_bas_vol", "sharpe_bas_vol", "secteurs_haut_vol",
         "sharpe_haut_vol", "anomalie_confirmee"],
        [[date_du_jour, n, ";".join(t for t, _ in tercile_bas_vol), round(sharpe_bas_vol, 3),
          ";".join(t for t, _ in tercile_haut_vol), round(sharpe_haut_vol, 3),
          anomalie_confirmee]],
    )

    print(f"OK -- tercile bas-vol {[t for t, _ in tercile_bas_vol]} Sharpe={sharpe_bas_vol:.3f} "
          f"vs tercile haut-vol {[t for t, _ in tercile_haut_vol]} Sharpe={sharpe_haut_vol:.3f} "
          f"-- anomalie low-vol {'confirmee' if anomalie_confirmee else 'non confirmee'} sur "
          f"cet echantillon (puissance statistique faible, n petit -- limite assumee)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
