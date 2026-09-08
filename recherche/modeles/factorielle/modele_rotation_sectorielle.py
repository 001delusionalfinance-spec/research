"""Modele -- rotation sectorielle, momentum 3 mois des 10 secteurs S&P 500 (ETF SPDR),
classement en leaders/retardataires.

Proxy de LEADERSHIP sectoriel, pas une lecture de phase de cycle automatique -- le classement
brut est objectif (qui surperforme), l'interpretation "early/late cycle" qu'on lui attache
habituellement en macro discretionnaire est une grille de lecture, pas rendue ici (coherent
avec MAP.md : ce depot produit une lecture, jamais une decision). Necessite l'extension
sectorielle de ingestion_yfinance_indices.py (2026-09-08, 10 ETF SPDR).
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "rotation_sectorielle"
FENETRE_JOURS = 91  # ~3 mois calendaires

SECTEURS = {
    "XLK": "Technologie", "XLF": "Finance", "XLE": "Energie", "XLV": "Sante",
    "XLI": "Industrie", "XLY": "Consommation discretionnaire", "XLP": "Consommation de base",
    "XLU": "Services collectifs", "XLB": "Materiaux", "XLRE": "Immobilier",
}


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    if len(serie) < 2:
        raise SerieVide("pas assez de points")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant")
    return candidats[-1]


def main() -> int:
    resultats = []
    echecs = []
    date_du_jour = None
    for ticker, nom in SECTEURS.items():
        try:
            serie = read_series(BRUT / "yfinance" / f"{ticker}.csv", value_col="close")
            date_du_jour = date_du_jour or serie[-1][0]
            prix_reference = valeur_n_jours_avant(serie, FENETRE_JOURS)
        except (SerieVide, FileNotFoundError) as e:
            echecs.append((ticker, str(e)))
            print(f"{ticker} : echec -- {e}")
            continue
        rendement = (serie[-1][1] / prix_reference - 1) * 100
        resultats.append((ticker, nom, round(rendement, 3)))

    if not resultats:
        print("echec -- aucun secteur exploitable")
        return 1

    resultats.sort(key=lambda r: r[2], reverse=True)
    lignes_csv = [[date_du_jour, rang + 1, ticker, nom, rendement]
                  for rang, (ticker, nom, rendement) in enumerate(resultats)]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "rang", "ticker", "secteur", "rendement_3m_pct"],
        lignes_csv,
    )

    print(f"OK -- classement momentum 3 mois ({len(resultats)} secteurs) :")
    for rang, (ticker, nom, rendement) in enumerate(resultats, 1):
        print(f"  {rang}. {nom} ({ticker}) : {rendement:+.2f}%")
    if echecs:
        print(f"{len(echecs)} secteur(s) exclu(s) : {[t for t, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
