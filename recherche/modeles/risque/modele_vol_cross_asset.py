"""Modele -- volatilite implicite comparee entre classes d'actifs.

Lit les six mesures de volatilite implicite ingerees : actions (VIX), Nasdaq (VXN), taux
(MOVE), petrole (OVX), or (GVZ) et volatilite de la volatilite (VVIX).

Ce que ca repond : **le stress est-il generalise ou localise ?** Un VIX eleve pendant que le
MOVE reste calme n'a pas le meme sens qu'une hausse simultanee des deux. Le premier cas est un
episode actions ; le second signale un stress de financement qui se propage. Et une hausse de
l'OVX seule pointe un choc d'offre energetique, pas une aversion au risque.

Chaque mesure est ramenee a son **rang en percentile sur cinq ans**, parce que leurs niveaux
absolus ne sont pas comparables entre eux -- un MOVE a 80 et un VIX a 80 ne decrivent pas le
meme degre de tension. Le percentile les rend comparables.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import (BRUT, ETAT, SerieVide, ecrire_csv,  # noqa: E402
                  percentile_rang, read_series)

NOM_MODELE = "vol_cross_asset"
VOL = BRUT / "marches" / "volatilite"

MESURES = [
    ("Actions US (VIX)", BRUT / "yfinance" / "VIX.csv", "close"),
    ("Nasdaq (VXN)", VOL / "VXN.csv", "close"),
    ("Taux US (MOVE)", VOL / "MOVE.csv", "close"),
    ("Petrole (OVX)", VOL / "OVX.csv", "close"),
    ("Or (GVZ)", VOL / "GVZ.csv", "close"),
    ("Vol de la vol (VVIX)", VOL / "VVIX.csv", "close"),
]
FENETRE_JOURS = 1260   # ~5 ans ouvres
SEUIL_TENDU = 80.0
SEUIL_CALME = 20.0


def main() -> int:
    lignes, echecs = [], []
    for libelle, chemin, colonne in MESURES:
        try:
            serie = read_series(chemin, colonne)
            fenetre = [v for _, v in serie][-FENETRE_JOURS:]
            if len(fenetre) < 250:
                raise SerieVide(f"seulement {len(fenetre)} points, moins d'un an d'historique")
            niveau = serie[-1][1]
            rang = percentile_rang(niveau, fenetre)
            if rang >= SEUIL_TENDU:
                etat = "tendu"
            elif rang <= SEUIL_CALME:
                etat = "calme"
            else:
                etat = "median"
            lignes.append((libelle, serie[-1][0], round(niveau, 2), round(rang, 1),
                           len(fenetre), etat))
        except (SerieVide, ValueError) as e:
            echecs.append((libelle, str(e)))

    if not lignes:
        print(f"echec -- aucune mesure exploitable ({len(echecs)} en erreur)")
        return 1

    lignes.sort(key=lambda l: -l[3])
    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["mesure", "date", "niveau", "percentile_5_ans", "n_observations", "etat"],
               lignes)

    tendus = [l[0] for l in lignes if l[5] == "tendu"]
    calmes = [l[0] for l in lignes if l[5] == "calme"]
    if len(tendus) >= 3:
        lecture = (f"stress GENERALISE -- {len(tendus)} mesures sur {len(lignes)} au-dessus du "
                   f"80e percentile ({', '.join(tendus)})")
    elif tendus:
        lecture = (f"stress LOCALISE sur {', '.join(tendus)} pendant que le reste ne l'est pas "
                   f"-- episode propre a cette classe d'actifs, pas une aversion au risque "
                   f"d'ensemble")
    elif len(calmes) >= 3:
        lecture = f"volatilite basse partout ({len(calmes)} mesures sous le 20e percentile)"
    else:
        lecture = "aucune classe d'actifs en tension marquee"

    detail = ", ".join(f"{l[0]} {l[3]:.0f}e pct" for l in lignes)
    print(f"OK -- {len(lignes)} mesures de volatilite : {detail} -- {lecture}")
    if echecs:
        print(f"   {len(echecs)} mesure(s) non exploitable(s) : {[n for n, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
