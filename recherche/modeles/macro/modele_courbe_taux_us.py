"""Modele -- courbe des taux US (spread 10 ans - 2 ans), signal de recession classique.

Une courbe inversee (spread negatif) a precede chacune des dernieres recessions US depuis les
annees 1970 -- pas une garantie causale, mais l'un des indicateurs macro les plus suivis et les
mieux documentes (Estrella & Mishkin 1998). Suit aussi depuis combien de jours consecutifs
l'inversion dure -- une inversion d'un jour et une inversion de 200 jours ne racontent pas la
meme histoire, meme si le spread instantane est similaire.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, lire_historique, read_series  # noqa: E402

NOM_MODELE = "courbe_taux_us"


def main() -> int:
    try:
        dgs10 = read_series(BRUT / "fred" / "DGS10.csv")
        dgs2 = read_series(BRUT / "fred" / "DGS2.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in dgs10) & set(d for d, _ in dgs2))
    if not dates_communes:
        print("echec -- aucune date commune entre DGS10 et DGS2")
        return 1

    map10, map2 = dict(dgs10), dict(dgs2)
    date_du_jour = dates_communes[-1]
    spread = map10[date_du_jour] - map2[date_du_jour]
    inversee = spread < 0

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "taux_10ans", "taux_2ans", "spread_pt", "inversee"],
        [[date_du_jour, map10[date_du_jour], map2[date_du_jour], round(spread, 3), inversee]],
    )

    try:
        historique = lire_historique(ETAT / f"{NOM_MODELE}.csv")
        jours_inversion_consecutifs = 0
        for ligne in reversed(historique):
            if ligne["inversee"] == "True":
                jours_inversion_consecutifs += 1
            else:
                break
    except SerieVide:
        jours_inversion_consecutifs = 1 if inversee else 0

    print(f"OK -- 10 ans={map10[date_du_jour]:.2f}%, 2 ans={map2[date_du_jour]:.2f}%, "
          f"spread={spread:+.2f}pt -- {'INVERSEE' if inversee else 'normale'} "
          f"({jours_inversion_consecutifs} run(s) consecutif(s) dans l'historique accumule)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
