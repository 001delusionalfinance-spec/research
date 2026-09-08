"""Modele -- ARIMA(1,1,1) sur le niveau du VIX, prevision a 1 jour -- via statsmodels
(estimation MLE, pas reimplemente a la main).

Ordre (1,1,1) choisi comme point de depart standard (differenciation d'ordre 1 pour la
non-stationnarite deja discutee ailleurs, AR(1)+MA(1) sur la serie differenciee) -- pas
selectionne par grid-search AIC ici (contrairement au VAR deja construit), volontairement
simple pour ce premier passage. Split train/test 80/20 pour evaluer honnêtement la prevision
1 jour, pas juste le fit in-sample.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "arima"
PART_TRAIN = 0.8


def main() -> int:
    try:
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    niveaux = valeurs(vix)
    date_du_jour = vix[-1][0]
    if len(niveaux) < 200:
        print("echec -- moins de 200 points")
        return 1

    n_train = int(len(niveaux) * PART_TRAIN)
    train, test = niveaux[:n_train], niveaux[n_train:]

    import numpy as np
    from statsmodels.tsa.arima.model import ARIMA

    modele = ARIMA(train, order=(1, 1, 1))
    resultat = modele.fit()

    # prevision 1-pas-a-la-fois sur le test set, en re-ajoutant chaque vraie valeur observee
    # avant de predire la suivante (evaluation honnete "1 jour en avant", pas une prevision
    # multi-jours qui accumulerait l'erreur)
    historique = list(train)
    erreurs = []
    for vraie_valeur in test[:100]:  # limite a 100 pas pour le temps de calcul (re-fit couteux)
        modele_pas = ARIMA(historique, order=(1, 1, 1))
        resultat_pas = modele_pas.fit()
        prediction = resultat_pas.forecast(steps=1)[0]
        erreurs.append((prediction - vraie_valeur) ** 2)
        historique.append(vraie_valeur)

    if not erreurs:
        print("echec -- aucune prevision realisee")
        return 1

    mse = sum(erreurs) / len(erreurs)
    rmse = mse ** 0.5

    # baseline naive : predire que demain = aujourd'hui (persistance)
    mse_naif = sum((a - b) ** 2 for a, b in zip(test[:len(erreurs)], test[1:len(erreurs) + 1])) \
        / len(erreurs)

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_previsions_test", "rmse_arima", "mse_naif", "bat_naif"],
        [[date_du_jour, len(erreurs), round(rmse, 4), round(mse_naif, 4), mse < mse_naif]],
    )

    print(f"OK -- ARIMA(1,1,1) sur {len(erreurs)} previsions 1-jour test : RMSE={rmse:.3f} "
          f"vs baseline naive MSE={mse_naif:.3f} -- "
          f"{'ARIMA bat' if mse < mse_naif else 'ARIMA NE BAT PAS'} la persistance simple")
    return 0


if __name__ == "__main__":
    sys.exit(main())
