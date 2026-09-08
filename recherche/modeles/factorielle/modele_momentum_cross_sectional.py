"""Modele -- momentum CROSS-SECTIONAL (pas time-series comme modele_momentum_prix.py) : spread
de rendement entre le tercile de secteurs les plus performants et le tercile les moins
performants sur 3 mois, 10 secteurs S&P 500.

C'est le vrai facteur momentum au sens academique (Jegadeesh-Titman 1993, Carhart 1997) --
achete les gagnants recents, vend les perdants recents, EN MEME TEMPS, sur le MEME univers a un
instant donne. Le "spread" (rendement du panier gagnant moins rendement du panier perdant) est
la mesure standard de la force du facteur ce mois-ci. Complete modele_rotation_sectorielle.py
(classement descriptif) en construisant le facteur lui-meme.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "momentum_cross_sectional"
FENETRE_JOURS = 91

SECTEURS = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE"]


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    if len(serie) < 2:
        raise SerieVide("pas assez de points")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant")
    return candidats[-1]


def main() -> int:
    rendements = {}
    date_du_jour = None
    for ticker in SECTEURS:
        try:
            serie = read_series(BRUT / "yfinance" / f"{ticker}.csv", value_col="close")
            date_du_jour = date_du_jour or serie[-1][0]
            prix_ref = valeur_n_jours_avant(serie, FENETRE_JOURS)
        except (SerieVide, FileNotFoundError) as e:
            print(f"{ticker} : echec -- {e}")
            continue
        rendements[ticker] = (serie[-1][1] / prix_ref - 1) * 100

    if len(rendements) < 6:
        print("echec -- moins de 6 secteurs exploitables, terciles non pertinents")
        return 1

    classes = sorted(rendements.items(), key=lambda kv: kv[1], reverse=True)
    n = len(classes)
    taille_tercile = n // 3
    tercile_gagnant = classes[:taille_tercile]
    tercile_perdant = classes[-taille_tercile:]

    rendement_gagnant = sum(r for _, r in tercile_gagnant) / len(tercile_gagnant)
    rendement_perdant = sum(r for _, r in tercile_perdant) / len(tercile_perdant)
    spread_momentum = rendement_gagnant - rendement_perdant

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "secteurs_gagnants", "rendement_gagnant_pct", "secteurs_perdants",
         "rendement_perdant_pct", "spread_momentum_pct"],
        [[date_du_jour, ";".join(t for t, _ in tercile_gagnant), round(rendement_gagnant, 3),
          ";".join(t for t, _ in tercile_perdant), round(rendement_perdant, 3),
          round(spread_momentum, 3)]],
    )

    print(f"OK -- panier gagnant {[t for t, _ in tercile_gagnant]} ({rendement_gagnant:+.2f}%) "
          f"vs panier perdant {[t for t, _ in tercile_perdant]} ({rendement_perdant:+.2f}%) -- "
          f"spread momentum={spread_momentum:+.2f}pt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
