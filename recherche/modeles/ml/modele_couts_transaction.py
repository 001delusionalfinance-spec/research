"""Modele -- impact des couts de transaction simules sur la strategie momentum 5j, meme
walk-forward que modele_walkforward_direction.py.

Meme sans position reelle a prendre ici (ce depot ne trade pas, cf. MAP.md), savoir si un
signal "survivrait" a des frais reels est une information de recherche legitime -- un signal
qui bat a peine la baseline brute peut devenir sans interet net de frais. Cout simule = 5pb par
changement de position (ordre de grandeur realiste pour un ETF liquide, pas mesure sur un
compte reel -- limite assumee). Un "trade" = un changement de direction predite d'un jour a
l'autre (pas une prediction correcte/incorrecte, juste un changement de cote).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "couts_transaction"
FENETRE_MOMENTUM = 5
MIN_HISTORIQUE_DEMARRAGE = 30
COUT_PAR_CHANGEMENT_BP = 5


def directions(prix: list) -> list:
    return [1 if b >= a else 0 for a, b in zip(prix[:-1], prix[1:])]


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    date_du_jour = sp500[-1][0]
    dirs_reelles = directions(prix)

    if len(dirs_reelles) < MIN_HISTORIQUE_DEMARRAGE + FENETRE_MOMENTUM + 10:
        print("echec -- historique insuffisant")
        return 1

    predictions = []
    rendements_reels = []
    for i in range(MIN_HISTORIQUE_DEMARRAGE, len(dirs_reelles)):
        if i < FENETRE_MOMENTUM:
            continue
        pred = 1 if prix[i] >= prix[i - FENETRE_MOMENTUM] else 0
        predictions.append(pred)
        rendement_jour = (prix[i + 1] / prix[i] - 1) if i + 1 < len(prix) else 0.0
        rendements_reels.append(rendement_jour)

    if len(predictions) < 30:
        print("echec -- pas assez de predictions")
        return 1

    n_changements = sum(1 for a, b in zip(predictions[:-1], predictions[1:]) if a != b)
    cout_par_changement = COUT_PAR_CHANGEMENT_BP / 10000

    # Rendement compose (equity curve), pas une somme simple -- une somme de rendements
    # journaliers sur 30 ans de donnees n'a pas d'interpretation directe en "valeur de
    # portefeuille", seul le compose en a une (convention standard de mesure de performance).
    valeur_brute = 1.0
    valeur_nette = 1.0
    for i, (p, r) in enumerate(zip(predictions, rendements_reels)):
        rendement_position = r if p == 1 else -r
        valeur_brute *= (1 + rendement_position)
        cout_jour = cout_par_changement if i > 0 and predictions[i] != predictions[i - 1] else 0.0
        valeur_nette *= (1 + rendement_position - cout_jour)

    rendement_strategie_brut = valeur_brute - 1
    rendement_strategie_net = valeur_nette - 1
    cout_total_pct = (valeur_brute - valeur_nette) / valeur_brute * 100 if valeur_brute != 0 \
        else None

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_predictions", "n_changements_position", "cout_total_pct",
         "rendement_cumule_brut_pct", "rendement_cumule_net_pct"],
        [[date_du_jour, len(predictions), n_changements, round(cout_total_pct, 2),
          round(rendement_strategie_brut * 100, 2), round(rendement_strategie_net * 100, 2)]],
    )

    print(f"OK -- {len(predictions)} predictions, {n_changements} changements de position "
          f"({COUT_PAR_CHANGEMENT_BP}pb/changement) -- rendement cumule brut="
          f"{rendement_strategie_brut*100:+.2f}%, cout total={cout_total_pct:.2f}%, "
          f"net={rendement_strategie_net*100:+.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
