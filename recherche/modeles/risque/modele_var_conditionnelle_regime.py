"""Modele -- VaR historique CONDITIONNELLE au regime de volatilite (VIX haut vs bas), pas une
VaR unique globale comme modele_var_drawdown.py.

Meme logique que modele_covar.py (deja construit) mais orientee "risque propre" plutot que
"risque systemique conditionnel a un autre marche" : ici, la VaR du S&P 500 lui-meme change
selon SON PROPRE regime de vol recent -- une VaR "moyenne" masque le fait que le vrai risque
encouru aujourd'hui depend du regime dans lequel on se trouve MAINTENANT, pas de la moyenne
sur tout l'historique.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, percentile_rang, read_series, rendements_log, valeurs  # noqa: E402

NOM_MODELE = "var_conditionnelle_regime"
FENETRE_REGIME = 20
SEUIL_VIX_HAUT_PERCENTILE = 66


def var_historique(rendements: list, seuil: float = 0.95) -> float:
    if len(rendements) < 20:
        raise SerieVide("moins de 20 rendements")
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
    if len(dates_communes) < 300:
        print("echec -- moins de 300 dates communes")
        return 1

    map_sp500, map_vix = dict(sp500), dict(vix)
    prix_sp500 = [map_sp500[d] for d in dates_communes]
    niveaux_vix = [map_vix[d] for d in dates_communes]

    rendements_sp500 = rendements_log(prix_sp500)
    vix_correspondant = niveaux_vix[1:]

    # regime actuel : VIX moyen des FENETRE_REGIME derniers jours, situe dans son propre
    # historique de percentile
    vix_recent_moyen = sum(niveaux_vix[-FENETRE_REGIME:]) / FENETRE_REGIME
    rang_vix_actuel = percentile_rang(vix_recent_moyen, niveaux_vix)
    regime_actuel_haut = rang_vix_actuel > SEUIL_VIX_HAUT_PERCENTILE

    seuil_vix_split = sorted(niveaux_vix)[int(len(niveaux_vix) * SEUIL_VIX_HAUT_PERCENTILE / 100)]
    rendements_regime_haut = [r for r, v in zip(rendements_sp500, vix_correspondant)
                               if v >= seuil_vix_split]
    rendements_regime_bas = [r for r, v in zip(rendements_sp500, vix_correspondant)
                              if v < seuil_vix_split]

    try:
        var_haut = var_historique(rendements_regime_haut)
        var_bas = var_historique(rendements_regime_bas)
        var_globale = var_historique(rendements_sp500)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    var_applicable = var_haut if regime_actuel_haut else var_bas
    date_du_jour = dates_communes[-1]

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "regime_vix_actuel", "rang_percentile_vix", "var95_regime_haut",
         "var95_regime_bas", "var95_globale", "var95_applicable_maintenant"],
        [[date_du_jour, "haut" if regime_actuel_haut else "bas", round(rang_vix_actuel, 1),
          round(var_haut * 100, 3), round(var_bas * 100, 3), round(var_globale * 100, 3),
          round(var_applicable * 100, 3)]],
    )

    print(f"OK -- regime VIX actuel={'haut' if regime_actuel_haut else 'bas'} "
          f"(rang percentile={rang_vix_actuel:.0f}) -- VaR95 applicable maintenant="
          f"{var_applicable*100:.2f}% (vs VaR95 globale non-conditionnelle="
          f"{var_globale*100:.2f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
