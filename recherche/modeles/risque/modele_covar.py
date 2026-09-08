"""Modele -- CoVaR simplifie (Adrian & Brunnermeier 2016, version simplifiee par quantile) :
VaR du S&P 500 CONDITIONNELLE a un VIX en detresse, vs VaR inconditionnelle.

VaR(SP500 | VIX dans son decile le plus haut) vs VaR(SP500) tout court -- Delta CoVaR = la
difference. Un Delta CoVaR fortement negatif = les pertes de queue s'aggravent nettement quand
le VIX est deja extreme (risque qui se transmet/s'amplifie), pas juste "en moyenne c'est pire".
Version simplifiee : pas de regression quantile formelle (la methode originale d'Adrian &
Brunnermeier), juste une comparaison de VaR historique entre deux sous-echantillons -- plus
simple, documente comme tel, pas presente comme la methode academique complete.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, percentile_rang, read_series, rendements_log  # noqa: E402

NOM_MODELE = "covar"
SEUIL_DETRESSE_PERCENTILE = 90


def var_historique(rendements: list, seuil: float = 0.95) -> float:
    if len(rendements) < 20:
        raise SerieVide("moins de 20 rendements -- VaR non fiable")
    r_tries = sorted(rendements)
    rang = int((1 - seuil) * len(r_tries))
    return r_tries[max(0, rang)]


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in sp500) & set(d for d, _ in vix))
    if len(dates_communes) < 100:
        print("echec -- moins de 100 dates communes")
        return 1

    map_sp500, map_vix = dict(sp500), dict(vix)
    prix_sp500 = [map_sp500[d] for d in dates_communes]
    niveaux_vix = [map_vix[d] for d in dates_communes]

    rendements_sp500 = rendements_log(prix_sp500)
    vix_correspondant = niveaux_vix[1:]  # aligne avec rendements_sp500[i] = jour dates[i+1]

    seuil_vix_detresse = sorted(niveaux_vix)[int(len(niveaux_vix) * SEUIL_DETRESSE_PERCENTILE / 100)]

    rendements_detresse = [r for r, v in zip(rendements_sp500, vix_correspondant)
                            if v >= seuil_vix_detresse]
    rendements_normal = [r for r, v in zip(rendements_sp500, vix_correspondant)
                          if v < seuil_vix_detresse]

    try:
        var_inconditionnelle = var_historique(rendements_sp500)
        var_detresse = var_historique(rendements_detresse)
        var_normal = var_historique(rendements_normal)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    delta_covar = var_detresse - var_normal
    date_du_jour = dates_communes[-1]

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "seuil_vix_detresse", "var95_inconditionnelle_pct", "var95_vix_detresse_pct",
         "var95_vix_normal_pct", "delta_covar_pct", "n_jours_detresse"],
        [[date_du_jour, round(seuil_vix_detresse, 2), round(var_inconditionnelle * 100, 3),
          round(var_detresse * 100, 3), round(var_normal * 100, 3),
          round(delta_covar * 100, 3), len(rendements_detresse)]],
    )

    print(f"OK -- VaR95 inconditionnelle={var_inconditionnelle*100:.2f}%, "
          f"VaR95|VIX detresse(>={seuil_vix_detresse:.1f})={var_detresse*100:.2f}%, "
          f"VaR95|VIX normal={var_normal*100:.2f}% -- DeltaCoVaR={delta_covar*100:+.2f}pt "
          f"({len(rendements_detresse)} jours de detresse dans l'echantillon)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
