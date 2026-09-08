"""Modele -- divergence positionnement/prix, S&P 500.

Signal classique : le prix monte mais le positionnement spéculatif net (COT) baisse en même
temps -- la hausse n'est pas portée par un excès de convictions spéculatives (au contraire,
elles refluent), lecture différente d'une hausse accompagnée d'un positionnement qui monte
aussi (peut signaler un excès qui se construit). Seul S&P 500 pour l'instant : c'est le seul
marché où `donnees/brut/` a A LA FOIS un prix (`yfinance/SP500.csv`) et un positionnement
(`cftc/SP500_EMINI.csv`) -- les autres marchés COT n'ont pas encore de série de prix ingérée.
"""

import csv
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "divergence_cot_prix"
FENETRE_JOURS = 30  # ~1 mois calendaire, comparable a la cadence hebdo des rapports COT


def lire_cot_net(path: Path) -> list:
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return [(l["date"], float(l["noncomm_net"])) for l in lignes]


def valeur_n_jours_avant(serie: list, n_jours: int):
    if len(serie) < 2:
        raise SerieVide("pas assez de points")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant")
    return candidats[-1]


def main() -> int:
    try:
        prix = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
        cot = lire_cot_net(BRUT / "cftc" / "SP500_EMINI.csv")
    except (SerieVide, FileNotFoundError) as e:
        print(f"echec -- {e}")
        return 1

    try:
        prix_reference = valeur_n_jours_avant(prix, FENETRE_JOURS)
        cot_reference = valeur_n_jours_avant(cot, FENETRE_JOURS)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix_actuel = prix[-1][1]
    cot_actuel = cot[-1][1]
    variation_prix_pct = (prix_actuel / prix_reference - 1) * 100
    variation_cot_pct = ((cot_actuel - cot_reference) / abs(cot_reference) * 100
                          if cot_reference != 0 else None)

    prix_monte = variation_prix_pct > 0
    cot_baisse = cot_actuel < cot_reference
    divergence = prix_monte and cot_baisse

    date_du_jour = prix[-1][0]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "variation_prix_pct", "cot_net_actuel", "cot_net_reference",
         "divergence_prix_hausse_cot_baisse"],
        [[date_du_jour, round(variation_prix_pct, 3), cot_actuel, cot_reference, divergence]],
    )

    print(f"OK -- SP500 {variation_prix_pct:+.2f}% sur {FENETRE_JOURS}j, "
          f"COT net {cot_reference:.0f} -> {cot_actuel:.0f} -- "
          f"{'DIVERGENCE (prix monte, positionnement recule)' if divergence else 'pas de divergence'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
