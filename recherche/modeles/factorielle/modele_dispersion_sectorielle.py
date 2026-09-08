"""Modele -- dispersion cross-sectionnelle des rendements sectoriels (S&P 500, 10 ETF SPDR).

Ecart-type des rendements 3 mois entre secteurs (deja calcules par modele_rotation_
sectorielle.py, recalcule ici independamment) -- une dispersion elevee signale un marche ou
la selection sectorielle "paie" (les secteurs divergent nettement), une dispersion faible
signale un marche domine par un facteur macro commun (tout bouge ensemble, peu de difference
entre secteurs). Concept standard de recherche factorielle (ex. utilise par les desks de
"style" pour juger si l'environnement favorise le stock/sector-picking).
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "dispersion_sectorielle"
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
    rendements = []
    date_du_jour = None
    for ticker in SECTEURS:
        try:
            serie = read_series(BRUT / "yfinance" / f"{ticker}.csv", value_col="close")
            date_du_jour = date_du_jour or serie[-1][0]
            prix_ref = valeur_n_jours_avant(serie, FENETRE_JOURS)
        except (SerieVide, FileNotFoundError) as e:
            print(f"{ticker} : echec -- {e}")
            continue
        rendements.append((serie[-1][1] / prix_ref - 1) * 100)

    if len(rendements) < 3:
        print("echec -- moins de 3 secteurs exploitables")
        return 1

    n = len(rendements)
    moyenne = sum(rendements) / n
    dispersion = (sum((r - moyenne) ** 2 for r in rendements) / n) ** 0.5
    etendue = max(rendements) - min(rendements)

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_secteurs", "rendement_moyen_pct", "dispersion_ecart_type_pct",
         "etendue_pct"],
        [[date_du_jour, n, round(moyenne, 3), round(dispersion, 3), round(etendue, 3)]],
    )

    print(f"OK -- {n} secteurs, rendement moyen 3m={moyenne:+.2f}%, "
          f"dispersion (ecart-type)={dispersion:.2f}pt, etendue={etendue:.2f}pt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
