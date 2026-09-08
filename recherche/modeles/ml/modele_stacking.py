"""Modele -- stacking simple : combine les predictions de 2 modeles deja construits (momentum
5j, modele_walkforward_direction.py ; et baseline majoritaire) via un poids APPRIS sur le train
(regression logistique manuelle par descente de gradient), pas un vote majoritaire fixe comme
modele_ensemble_signaux.py.

Split train/test strict 70/30 (temporel) -- le poids de combinaison est appris UNIQUEMENT sur
train, jamais reajuste en voyant le test. Descente de gradient simple (pas de librairie ML,
2 parametres seulement -- poids + biais, pas besoin de plus).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "stacking"
FENETRE_MOMENTUM = 5
PART_TRAIN = 0.7
TAUX_APPRENTISSAGE = 0.1
N_ITERATIONS = 500


def directions(prix: list) -> list:
    return [1 if b >= a else 0 for a, b in zip(prix[:-1], prix[1:])]


def sigmoid(z: float) -> float:
    import math
    z = max(-30, min(30, z))  # evite l'overflow -- clamp, pas une exception pour un cas
                                # numeriquement normal
    return 1 / (1 + math.exp(-z))


def entrainer_logistique(pred_momentum: list, pred_baseline: list, y: list) -> tuple:
    """2 features binaires (0/1) -> poids w_momentum, w_baseline, biais, appris par descente de
    gradient sur la log-vraisemblance (regression logistique standard, a la main -- 2
    parametres, pas besoin de librairie)."""
    n = len(y)
    if n < 30:
        raise SerieVide("moins de 30 points d'entrainement")
    w_m, w_b, biais = 0.0, 0.0, 0.0
    for _ in range(N_ITERATIONS):
        grad_m, grad_b, grad_biais = 0.0, 0.0, 0.0
        for pm, pb, yi in zip(pred_momentum, pred_baseline, y):
            z = w_m * pm + w_b * pb + biais
            erreur = sigmoid(z) - yi
            grad_m += erreur * pm
            grad_b += erreur * pb
            grad_biais += erreur
        w_m -= TAUX_APPRENTISSAGE * grad_m / n
        w_b -= TAUX_APPRENTISSAGE * grad_b / n
        biais -= TAUX_APPRENTISSAGE * grad_biais / n
    return w_m, w_b, biais


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    date_du_jour = sp500[-1][0]
    dirs_reelles = directions(prix)

    debut = 30
    if len(dirs_reelles) < debut + FENETRE_MOMENTUM + 60:
        print("echec -- historique insuffisant")
        return 1

    pred_momentum, pred_baseline, y = [], [], []
    for i in range(debut, len(dirs_reelles)):
        if i < FENETRE_MOMENTUM:
            continue
        pred_momentum.append(1 if prix[i] >= prix[i - FENETRE_MOMENTUM] else 0)
        hausses_avant = sum(dirs_reelles[:i])
        pred_baseline.append(1 if hausses_avant >= i / 2 else 0)
        y.append(dirs_reelles[i])

    n_total = len(y)
    n_train = int(n_total * PART_TRAIN)
    if n_train < 30 or n_total - n_train < 30:
        print("echec -- split train/test insuffisant")
        return 1

    try:
        w_m, w_b, biais = entrainer_logistique(
            pred_momentum[:n_train], pred_baseline[:n_train], y[:n_train])
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    correct_stacking, correct_momentum_seul, correct_baseline_seule = 0, 0, 0
    for i in range(n_train, n_total):
        z = w_m * pred_momentum[i] + w_b * pred_baseline[i] + biais
        pred_stacking = 1 if sigmoid(z) >= 0.5 else 0
        correct_stacking += int(pred_stacking == y[i])
        correct_momentum_seul += int(pred_momentum[i] == y[i])
        correct_baseline_seule += int(pred_baseline[i] == y[i])

    n_test = n_total - n_train
    acc_stacking = correct_stacking / n_test
    acc_momentum = correct_momentum_seul / n_test
    acc_baseline = correct_baseline_seule / n_test

    date_du_jour_final = date_du_jour
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "poids_momentum", "poids_baseline", "biais", "n_test",
         "accuracy_stacking", "accuracy_momentum_seul", "accuracy_baseline_seule"],
        [[date_du_jour_final, round(w_m, 4), round(w_b, 4), round(biais, 4), n_test,
          round(acc_stacking, 4), round(acc_momentum, 4), round(acc_baseline, 4)]],
    )

    bat_baseline = acc_stacking > acc_baseline
    scores = [("stacking", acc_stacking), ("momentum seul", acc_momentum), ("baseline", acc_baseline)]
    meilleure_acc = max(v for _, v in scores)
    meilleurs = [nom for nom, v in scores if v == meilleure_acc]
    meilleur = " / ".join(meilleurs) + (" (ex-aequo)" if len(meilleurs) > 1 else "")
    print(f"OK -- poids appris (momentum={w_m:.3f}, baseline={w_b:.3f}, biais={biais:.3f}) -- "
          f"accuracy stacking={acc_stacking:.4f} vs momentum seul={acc_momentum:.4f}, "
          f"baseline seule={acc_baseline:.4f} sur {n_test} points test -- stacking "
          f"{'BAT' if bat_baseline else 'NE BAT PAS'} la baseline, meilleur={meilleur}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
