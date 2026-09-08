"""Modele -- decision stump (arbre de decision a un seul seuil, la brique de base d'un
gradient boosting/random forest) sur variation_vix, walk-forward strict -- teste si un seuil
NON-LINEAIRE simple bat la regression lineaire deja construite (modele_prevision_vol_regression.py,
modele_regression_multifeatures.py) sur la meme question.

Seuil optimal cherche UNIQUEMENT sur le train (jamais recalcule en voyant le test, meme
discipline que modele_test_overfitting.py) parmi les percentiles 10/20/.../90 de la feature sur
le train -- pas un vrai arbre CART complet (un seul niveau, une seule feature), suffisant pour
tester l'hypothese "un seuil simple capture-t-il quelque chose qu'une droite ne capture pas".
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "decision_stump"
MIN_HISTORIQUE_DEMARRAGE = 30


def directions(prix: list) -> list:
    return [1 if b >= a else 0 for a, b in zip(prix[:-1], prix[1:])]


def meilleur_seuil(variations_vix_train: list, y_train: list) -> tuple:
    """Cherche le seuil (parmi les deciles de la feature) qui maximise l'accuracy sur le train
    -- retourne (seuil, sens : True si "variation < seuil -> predit 1")."""
    if len(variations_vix_train) < 30:
        raise SerieVide("moins de 30 points train")
    valeurs_triees = sorted(variations_vix_train)
    candidats = [valeurs_triees[int(len(valeurs_triees) * p / 10)] for p in range(1, 10)]

    meilleur_score, meilleur_seuil_val, meilleur_sens = -1, None, None
    for seuil in candidats:
        for sens in (True, False):
            correct = 0
            for v, y in zip(variations_vix_train, y_train):
                pred = 1 if (v < seuil) == sens else 0
                correct += int(pred == y)
            score = correct / len(y_train)
            if score > meilleur_score:
                meilleur_score, meilleur_seuil_val, meilleur_sens = score, seuil, sens
    return meilleur_seuil_val, meilleur_sens


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
    prix = [map_sp500[d] for d in dates_communes]
    niveaux_vix = [map_vix[d] for d in dates_communes]
    date_du_jour = dates_communes[-1]

    dirs_reelles = directions(prix)
    # variations_vix[i] = niveaux_vix[i] - niveaux_vix[i-1] (mouvement CONNU avant de predire
    # dirs_reelles[i], qui compare prix[i] a prix[i+1]) -- pas niveaux_vix[i+1]-niveaux_vix[i]
    # (meme intervalle que dirs_reelles[i], fuite temporelle -- meme bug reel trouve et corrige
    # dans modele_screening_features.py le meme jour, ici corrige des l'ecriture initiale)
    variations_vix = [niveaux_vix[i] - niveaux_vix[i - 1] for i in range(1, len(niveaux_vix))]
    dirs_reelles = dirs_reelles[1:]  # aligne : dirs_reelles[0] n'a pas de variation_vix
                                       # correspondante (pas de niveau i-1 = -1)

    n_total = min(len(dirs_reelles), len(variations_vix))
    dirs_reelles, variations_vix = dirs_reelles[:n_total], variations_vix[:n_total]

    n_train = int(n_total * 0.7)
    if n_train < 30 or n_total - n_train < 30:
        print("echec -- split train/test insuffisant")
        return 1

    try:
        seuil, sens = meilleur_seuil(variations_vix[:n_train], dirs_reelles[:n_train])
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    correct_stump, correct_baseline = 0, 0
    for i in range(n_train, n_total):
        pred_stump = 1 if (variations_vix[i] < seuil) == sens else 0
        hausses_avant = sum(dirs_reelles[:i])
        pred_baseline = 1 if hausses_avant >= i / 2 else 0
        correct_stump += int(pred_stump == dirs_reelles[i])
        correct_baseline += int(pred_baseline == dirs_reelles[i])

    n_test = n_total - n_train
    acc_stump = correct_stump / n_test
    acc_baseline = correct_baseline / n_test

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "seuil_appris", "sens", "n_test", "accuracy_stump", "accuracy_baseline"],
        [[date_du_jour, round(seuil, 4), sens, n_test, round(acc_stump, 4),
          round(acc_baseline, 4)]],
    )

    print(f"OK -- seuil appris={seuil:.3f} (sens={sens}) -- accuracy stump={acc_stump:.4f} vs "
          f"baseline={acc_baseline:.4f} sur {n_test} points test -- "
          f"{'stump BAT' if acc_stump > acc_baseline else 'stump NE BAT PAS'} la baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
