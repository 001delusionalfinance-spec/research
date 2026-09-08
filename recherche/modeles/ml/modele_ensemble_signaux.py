"""Modele -- ensemble simple (vote majoritaire) combinant momentum 5j et variation du VIX,
walk-forward strict -- suite logique de modele_screening_features.py (variation_vix etait
ressortie fortement significative, momentum_5j faiblement).

Deux regles individuelles + leur vote combine, toutes les trois evaluees walk-forward avec la
MEME discipline que modele_walkforward_direction.py. Regle VIX : une variation VIX negative
aujourd'hui (marche qui se detend) vote hausse demain (coherent avec le signe negatif trouve
dans le screening) ; positive vote baisse. En cas de desaccord entre les deux regles, le vote
penche vers celle historiquement la plus fiable (VIX, d'apres le screening) -- tie-break
documente, pas cache.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "ensemble_signaux"
FENETRE_MOMENTUM = 5
MIN_HISTORIQUE_DEMARRAGE = 30


def directions(prix: list) -> list:
    return [1 if b >= a else 0 for a, b in zip(prix[:-1], prix[1:])]


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in sp500) & set(d for d, _ in vix))
    if len(dates_communes) < MIN_HISTORIQUE_DEMARRAGE + FENETRE_MOMENTUM + 10:
        print("echec -- historique insuffisant")
        return 1

    map_sp500, map_vix = dict(sp500), dict(vix)
    prix = [map_sp500[d] for d in dates_communes]
    niveaux_vix = [map_vix[d] for d in dates_communes]

    dirs_reelles = directions(prix)  # dirs_reelles[i] = direction de dates[i+1] vs dates[i]

    correct_momentum, correct_vix, correct_ensemble, correct_baseline = 0, 0, 0, 0
    n_predictions = 0

    for i in range(MIN_HISTORIQUE_DEMARRAGE, len(dirs_reelles)):
        if i < FENETRE_MOMENTUM or i < 1:
            continue
        pred_momentum = 1 if prix[i] >= prix[i - FENETRE_MOMENTUM] else 0
        variation_vix_jour = niveaux_vix[i] - niveaux_vix[i - 1]
        pred_vix = 1 if variation_vix_jour < 0 else 0

        if pred_momentum == pred_vix:
            pred_ensemble = pred_momentum
        else:
            pred_ensemble = pred_vix  # tie-break vers VIX, cf. docstring

        hausses_avant = sum(dirs_reelles[:i])
        pred_baseline = 1 if hausses_avant >= i / 2 else 0

        reel = dirs_reelles[i]
        correct_momentum += int(pred_momentum == reel)
        correct_vix += int(pred_vix == reel)
        correct_ensemble += int(pred_ensemble == reel)
        correct_baseline += int(pred_baseline == reel)
        n_predictions += 1

    if n_predictions == 0:
        print("echec -- aucune prediction realisable")
        return 1

    acc_momentum = correct_momentum / n_predictions
    acc_vix = correct_vix / n_predictions
    acc_ensemble = correct_ensemble / n_predictions
    acc_baseline = correct_baseline / n_predictions

    date_du_jour = dates_communes[-1]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_predictions", "accuracy_momentum", "accuracy_vix", "accuracy_ensemble",
         "accuracy_baseline"],
        [[date_du_jour, n_predictions, round(acc_momentum, 4), round(acc_vix, 4),
          round(acc_ensemble, 4), round(acc_baseline, 4)]],
    )

    bat_baseline = acc_ensemble > acc_baseline
    print(f"OK -- {n_predictions} predictions -- momentum={acc_momentum:.4f}, "
          f"vix={acc_vix:.4f}, ensemble={acc_ensemble:.4f}, baseline={acc_baseline:.4f} -- "
          f"ensemble {'BAT' if bat_baseline else 'NE BAT PAS'} la baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
