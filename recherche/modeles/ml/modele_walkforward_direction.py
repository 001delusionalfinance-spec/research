"""Modele -- prediction de la direction du S&P 500 (hausse/baisse), walk-forward strict.

Discipline reprise de GMDC (Q1 famille 6, ML) : validation walk-forward uniquement (pour
predire le jour t+1, n'utilise jamais une donnee posterieure a t -- aucune fuite d'information
du futur), comparaison honnete a une baseline naive, resultat rapporte tel quel meme si le
modele ne bat pas la baseline (GMDC : "le modele (59.0%) NE BAT PAS la baseline naive (59.2%)"
-- documente comme un resultat, pas cache).

Regle testee ici, volontairement simple (pas de librairie ML -- stdlib seulement) : momentum de
continuation a 5 jours -- predit hausse demain si le rendement des 5 derniers jours est positif,
baisse sinon. Baseline : classe majoritaire observee jusqu'a la veille (jamais le futur).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "walkforward_direction_sp500"
FENETRE_MOMENTUM = 5
MIN_HISTORIQUE_DEMARRAGE = 30  # avant ce point, pas assez d'historique pour une baseline
                                # de classe majoritaire fiable -- exclu du walk-forward, pas
                                # remplace par une valeur arbitraire


def directions(prix: list) -> list:
    """1 si hausse (ou egalite), 0 si baisse -- jour par jour."""
    return [1 if b >= a else 0 for a, b in zip(prix[:-1], prix[1:])]


def predire_momentum(prix_jusqu_a_t: list, fenetre: int) -> int:
    if len(prix_jusqu_a_t) <= fenetre:
        raise SerieVide("pas assez d'historique pour le momentum")
    return 1 if prix_jusqu_a_t[-1] >= prix_jusqu_a_t[-1 - fenetre] else 0


def predire_baseline(directions_jusqu_a_t_moins_1: list) -> int:
    """Classe majoritaire observee STRICTEMENT avant le jour predit -- jamais la classe du jour
    lui-meme ni d'apres, sinon ce n'est plus walk-forward."""
    if not directions_jusqu_a_t_moins_1:
        raise SerieVide("aucun historique de direction disponible")
    hausses = sum(directions_jusqu_a_t_moins_1)
    return 1 if hausses >= len(directions_jusqu_a_t_moins_1) / 2 else 0


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    dates = [d for d, _ in sp500]
    dirs_reelles = directions(prix)  # dirs_reelles[i] = direction du jour dates[i+1]

    if len(dirs_reelles) < MIN_HISTORIQUE_DEMARRAGE + FENETRE_MOMENTUM + 1:
        print("echec -- historique insuffisant pour un walk-forward significatif")
        return 1

    debut = MIN_HISTORIQUE_DEMARRAGE
    correct_momentum = 0
    correct_baseline = 0
    n_predictions = 0

    for i in range(debut, len(dirs_reelles)):
        # au moment de predire dirs_reelles[i] (direction de prix[i+1] vs prix[i]), seules les
        # donnees jusqu'a prix[i] (inclus) sont disponibles -- jamais prix[i+1].
        prix_disponibles = prix[:i + 1]
        dirs_disponibles = dirs_reelles[:i]  # directions strictement avant celle predite

        try:
            pred_mom = predire_momentum(prix_disponibles, FENETRE_MOMENTUM)
            pred_base = predire_baseline(dirs_disponibles)
        except SerieVide:
            continue

        n_predictions += 1
        correct_momentum += int(pred_mom == dirs_reelles[i])
        correct_baseline += int(pred_base == dirs_reelles[i])

    if n_predictions == 0:
        print("echec -- aucune prediction walk-forward realisable")
        return 1

    acc_momentum = correct_momentum / n_predictions
    acc_baseline = correct_baseline / n_predictions
    bat_baseline = acc_momentum > acc_baseline

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_predictions", "accuracy_momentum_5j", "accuracy_baseline_majoritaire",
         "bat_la_baseline"],
        [[dates[-1], n_predictions, round(acc_momentum, 4), round(acc_baseline, 4),
          bat_baseline]],
    )

    verdict = "BAT la baseline" if bat_baseline else "NE BAT PAS la baseline"
    print(f"OK -- {n_predictions} predictions walk-forward -- momentum 5j={acc_momentum:.4f} "
          f"vs baseline majoritaire={acc_baseline:.4f} -- {verdict} (resultat honnete, pas "
          f"ajuste pour paraitre mieux)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
