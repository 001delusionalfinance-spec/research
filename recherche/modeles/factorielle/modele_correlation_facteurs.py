"""Modele -- correlation entre facteurs deja construits : momentum sectoriel (spread gagnant-
perdant) vs beta au VIX -- est-ce que le momentum sectoriel est plus fort quand le marche est
plus sensible a la vol (regime "risque"), ou independant ?

Pas une nouvelle donnee -- recombine modele_momentum_cross_sectional.py (recalcule ici pour
chaque secteur individuellement, pas juste les terciles extremes) et l'idee de sensibilite au
VIX (modele_beta_vol.py, applique ici par secteur). Question de recherche factorielle standard :
les facteurs sont-ils eux-memes correles entre eux (ce qui reduirait la diversification reelle
d'une strategie qui les combinerait) ?
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, correlation, read_series, rendements_log  # noqa: E402

NOM_MODELE = "correlation_facteurs"
FENETRE_MOMENTUM = 91
FENETRE_BETA = 60

SECTEURS = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE"]


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    if len(serie) < 2:
        raise SerieVide("pas assez de points")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant")
    return candidats[-1]


def beta_vol_secteur(serie_secteur: list, vix: list) -> float:
    dates_communes = sorted(set(d for d, _ in serie_secteur) & set(d for d, _ in vix))
    map_s, map_v = dict(serie_secteur), dict(vix)
    prix = [map_s[d] for d in dates_communes][-FENETRE_BETA - 1:]
    niveaux_vix = [map_v[d] for d in dates_communes][-FENETRE_BETA - 1:]
    rendements = rendements_log(prix)
    variations_vix = [b - a for a, b in zip(niveaux_vix[:-1], niveaux_vix[1:])]
    n = min(len(rendements), len(variations_vix))
    if n < 10:
        raise SerieVide("pas assez de points communs")
    rendements, variations_vix = rendements[-n:], variations_vix[-n:]
    mx = sum(variations_vix) / n
    my = sum(rendements) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(variations_vix, rendements))
    var_x = sum((x - mx) ** 2 for x in variations_vix)
    if var_x == 0:
        raise SerieVide("variance nulle")
    return cov / var_x


def main() -> int:
    try:
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    momentums, betas = {}, {}
    date_du_jour = None
    for ticker in SECTEURS:
        try:
            serie = read_series(BRUT / "yfinance" / f"{ticker}.csv", value_col="close")
            date_du_jour = date_du_jour or serie[-1][0]
            prix_ref = valeur_n_jours_avant(serie, FENETRE_MOMENTUM)
            momentums[ticker] = (serie[-1][1] / prix_ref - 1) * 100
            betas[ticker] = beta_vol_secteur(serie, vix)
        except (SerieVide, FileNotFoundError) as e:
            print(f"{ticker} : echec -- {e}")
            continue

    tickers_communs = sorted(set(momentums) & set(betas))
    if len(tickers_communs) < 5:
        print("echec -- moins de 5 secteurs exploitables")
        return 1

    vals_momentum = [momentums[t] for t in tickers_communs]
    vals_beta = [betas[t] for t in tickers_communs]

    try:
        corr = correlation(vals_momentum, vals_beta)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_secteurs", "correlation_momentum_beta_vix"],
        [[date_du_jour, len(tickers_communs), round(corr, 4)]],
    )

    print(f"OK -- correlation entre momentum 3m et beta-VIX, {len(tickers_communs)} secteurs : "
          f"{corr:+.3f} ({'facteurs lies (diversification reduite)' if abs(corr) > 0.4 else 'facteurs largement independants'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
