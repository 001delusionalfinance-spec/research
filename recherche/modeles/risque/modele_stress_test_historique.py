"""Modele -- stress testing par scenario historique reel (2008, 2020), S&P 500.

Rejoue le pire drawdown peak-to-trough observe pendant chaque crise sur le niveau ACTUEL du
S&P 500 -- "si un choc de la meme AMPLITUDE RELATIVE survenait aujourd'hui, a quel niveau ca
mettrait l'indice". Necessite l'historique etendu a 30 ans de ingestion_yfinance_indices.py
(2026-09-08) -- avant cette extension (2 ans), 2008/2020 n'etaient simplement pas dans les
donnees disponibles.

Fenetres de crise codees en dur (dates de debut/fin du pic au creux, verifiees contre des
faits de marche connus, pas devinees) :
- GFC 2008 : pic 2007-10-09, creux 2009-03-09
- COVID 2020 : pic 2020-02-19, creux 2020-03-23
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "stress_test_historique"

SCENARIOS = {
    "GFC_2008": ("2007-10-09", "2009-03-09"),
    "COVID_2020": ("2020-02-19", "2020-03-23"),
}


def valeur_a_date_la_plus_proche(serie_par_date: dict, dates_triees: list, cible: str) -> float:
    """La date exacte demandee peut ne pas exister (jour ferie/weekend) -- prend la plus
    proche disponible, jamais une extrapolation."""
    if cible in serie_par_date:
        return serie_par_date[cible]
    candidats = [d for d in dates_triees if d <= cible]
    if not candidats:
        raise SerieVide(f"aucune donnee disponible avant {cible}")
    return serie_par_date[candidats[-1]]


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    serie_par_date = dict(sp500)
    dates_triees = sorted(serie_par_date.keys())
    prix_actuel = sp500[-1][1]
    date_du_jour = sp500[-1][0]

    resultats = []
    echecs = []
    for nom_scenario, (date_pic, date_creux) in SCENARIOS.items():
        try:
            prix_pic = valeur_a_date_la_plus_proche(serie_par_date, dates_triees, date_pic)
            prix_creux = valeur_a_date_la_plus_proche(serie_par_date, dates_triees, date_creux)
        except SerieVide as e:
            echecs.append((nom_scenario, str(e)))
            print(f"{nom_scenario} : echec -- {e}")
            continue

        chute_pct = (prix_creux / prix_pic - 1) * 100
        niveau_rejoue = prix_actuel * (1 + chute_pct / 100)
        resultats.append([date_du_jour, nom_scenario, date_pic, date_creux,
                           round(chute_pct, 2), round(niveau_rejoue, 2)])
        print(f"{nom_scenario} ({date_pic} -> {date_creux}) : chute historique={chute_pct:.1f}% "
              f"-- rejouee sur le niveau actuel ({prix_actuel:.0f}) -> {niveau_rejoue:.0f}")

    if not resultats:
        print("echec -- aucun scenario exploitable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "scenario", "date_pic", "date_creux", "chute_pct", "niveau_sp500_rejoue"],
        resultats,
    )
    if echecs:
        print(f"{len(echecs)} scenario(s) exclu(s) : {[s for s, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
