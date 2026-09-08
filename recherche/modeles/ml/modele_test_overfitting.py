"""Modele -- demonstration explicite d'overfitting : recherche de parametre in-sample vs
walk-forward honnete, meme regle (momentum de continuation) que modele_walkforward_direction.py.

modele_walkforward_direction.py teste UNE fenetre fixee a l'avance (5j) en walk-forward pur.
Ici, la meme famille de regle (momentum sur N jours) est D'ABORD "optimisee" en cherchant le
meilleur N sur TOUT l'historique a la fois (in-sample, exactement l'erreur classique d'un
backtest naif qui essaie plusieurs parametres et garde le meilleur) puis reevaluee en
walk-forward strict avec ce N "gagnant". L'ecart entre les deux chiffres EST la demonstration :
si l'in-sample est nettement meilleur que le walk-forward avec le meme N, c'est la signature
d'un choix de parametre qui a appris le bruit de l'echantillon, pas un vrai edge.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "test_overfitting_momentum"
FENETRES_TESTEES = list(range(2, 31))
MIN_HISTORIQUE_DEMARRAGE = 30


def directions(prix: list) -> list:
    return [1 if b >= a else 0 for a, b in zip(prix[:-1], prix[1:])]


def accuracy_in_sample(prix: list, dirs_reelles: list, fenetre: int) -> float:
    """Regle evaluee sur TOUT l'historique en meme temps -- in-sample, pas walk-forward. Sert
    uniquement a demontrer le biais, jamais a choisir un parametre de production."""
    correct, total = 0, 0
    for i in range(fenetre, len(dirs_reelles)):
        pred = 1 if prix[i] >= prix[i - fenetre] else 0
        correct += int(pred == dirs_reelles[i])
        total += 1
    if total == 0:
        raise SerieVide(f"aucune prediction possible pour la fenetre {fenetre}")
    return correct / total


def accuracy_walk_forward(prix: list, dirs_reelles: list, fenetre: int, debut: int) -> float:
    """Meme discipline stricte que modele_walkforward_direction.py -- jamais de donnee du
    futur au moment de predire."""
    correct, total = 0, 0
    for i in range(debut, len(dirs_reelles)):
        if i < fenetre:
            continue
        pred = 1 if prix[i] >= prix[i - fenetre] else 0  # prix[i] = disponible au moment de
                                                            # predire dirs_reelles[i] (direction
                                                            # de prix[i+1] vs prix[i])
        correct += int(pred == dirs_reelles[i])
        total += 1
    if total == 0:
        raise SerieVide(f"aucune prediction walk-forward possible pour la fenetre {fenetre}")
    return correct / total


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    date_du_jour = sp500[-1][0]
    dirs_reelles = directions(prix)

    if len(dirs_reelles) < MIN_HISTORIQUE_DEMARRAGE + max(FENETRES_TESTEES) + 1:
        print("echec -- historique insuffisant")
        return 1

    resultats_in_sample = {}
    for f in FENETRES_TESTEES:
        try:
            resultats_in_sample[f] = accuracy_in_sample(prix, dirs_reelles, f)
        except SerieVide:
            continue

    if not resultats_in_sample:
        print("echec -- aucune fenetre exploitable in-sample")
        return 1

    meilleure_fenetre = max(resultats_in_sample, key=resultats_in_sample.get)
    meilleure_accuracy_in_sample = resultats_in_sample[meilleure_fenetre]

    try:
        accuracy_wf = accuracy_walk_forward(prix, dirs_reelles, meilleure_fenetre,
                                              MIN_HISTORIQUE_DEMARRAGE)
    except SerieVide as e:
        print(f"echec walk-forward -- {e}")
        return 1

    ecart = meilleure_accuracy_in_sample - accuracy_wf
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "meilleure_fenetre_jours", "accuracy_in_sample", "accuracy_walk_forward",
         "ecart_overfitting"],
        [[date_du_jour, meilleure_fenetre, round(meilleure_accuracy_in_sample, 4),
          round(accuracy_wf, 4), round(ecart, 4)]],
    )

    print(f"OK -- meilleure fenetre in-sample={meilleure_fenetre}j (accuracy="
          f"{meilleure_accuracy_in_sample:.4f}) vs meme fenetre en walk-forward="
          f"{accuracy_wf:.4f} -- ecart={ecart:+.4f} "
          f"({'signature d overfitting' if ecart > 0.02 else 'ecart faible'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
