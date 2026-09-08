"""Modele -- screening de features (correlation point-bisериale avec la direction J+1 du
S&P 500), etape prealable a tout modele ML -- savoir quelles features ont ne serait-ce qu'un
lien univarie avant d'en construire un modele combine.

4 features candidates testees : momentum 5j, momentum 20j, niveau du VIX, variation du VIX --
chacune correlee a la direction binaire (0/1) du rendement suivant via un test t (scipy, meme
fonction que _lib.correlation_avec_p_valeur, appliquee ici a une variable binaire -- test
point-biserial, cas particulier valide du Pearson standard). Walk-forward NON applicable ici
(ce n'est pas une prediction, un screening descriptif sur tout l'echantillon) -- a associer a
modele_walkforward_direction.py si une feature ressort comme prometteuse.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import (BRUT, ETAT, SerieVide, accumuler_csv, correlation_avec_p_valeur,  # noqa: E402
                   read_series, rendements_log, valeurs)

NOM_MODELE = "screening_features"


def directions(prix: list) -> list:
    return [1 if b >= a else 0 for a, b in zip(prix[:-1], prix[1:])]


def momentum_n_jours(prix: list, n: int) -> list:
    """rendement sur n jours, aligne pour correspondre a directions[i] = direction de
    prix[i+1] vs prix[i] -- momentum_n_jours[i] doit etre connu AVANT de predire directions[i],
    donc calcule jusqu'a prix[i] inclus (indice i dans prix, pas i+1)."""
    out = []
    for i in range(len(prix) - 1):
        if i < n:
            out.append(None)
        else:
            out.append((prix[i] - prix[i - n]) / prix[i - n])
    return out


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in sp500) & set(d for d, _ in vix))
    if len(dates_communes) < 100:
        print("echec -- pas assez de dates communes")
        return 1

    map_sp500, map_vix = dict(sp500), dict(vix)
    prix_sp500 = [map_sp500[d] for d in dates_communes]
    niveaux_vix = [map_vix[d] for d in dates_communes]
    date_du_jour = dates_communes[-1]

    dirs = directions(prix_sp500)
    mom5 = momentum_n_jours(prix_sp500, 5)
    mom20 = momentum_n_jours(prix_sp500, 20)
    vix_niveau = niveaux_vix[:-1]
    vix_variation = [b - a for a, b in zip(niveaux_vix[:-1], niveaux_vix[1:])]

    features = {
        "momentum_5j": mom5,
        "momentum_20j": mom20,
        "niveau_vix": vix_niveau,
        "variation_vix": vix_variation,
    }

    resultats = []
    for nom_feature, valeurs_feature in features.items():
        paires_valides = [(f, d) for f, d in zip(valeurs_feature, dirs) if f is not None]
        if len(paires_valides) < 30:
            print(f"{nom_feature} : echec -- moins de 30 paires valides")
            continue
        f_vals = [p[0] for p in paires_valides]
        d_vals = [float(p[1]) for p in paires_valides]
        try:
            r, p = correlation_avec_p_valeur(f_vals, d_vals)
        except SerieVide as e:
            print(f"{nom_feature} : echec -- {e}")
            continue
        significatif = p < 0.05
        resultats.append([date_du_jour, nom_feature, round(r, 4), round(p, 4), significatif])
        marque = " *" if significatif else ""
        print(f"{nom_feature} : r={r:+.4f}, p={p:.4f}{marque}")

    if not resultats:
        print("echec -- aucune feature exploitable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "feature", "correlation", "p_valeur", "significatif"],
        resultats,
    )
    n_sig = sum(1 for r in resultats if r[4])
    print(f"\n{n_sig}/{len(resultats)} features avec un lien univarie significatif (p<0.05, "
          f"sans correction multiple-testing ici -- seulement 4 tests)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
