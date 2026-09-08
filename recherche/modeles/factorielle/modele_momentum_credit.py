"""Modele -- momentum de prix applique au SPREAD DE CREDIT high-yield (pas un prix d'actif) --
meme technique 12-1 mois que modele_momentum_prix.py (Jegadeesh-Titman), nouvel underlying.

Un spread qui se resserre en tendance (momentum negatif au sens du niveau, mais "ameliore" au
sens du risque) a une lecture differente d'un spread stable ou qui s'ecarte -- capture la
DYNAMIQUE du facteur qualite credit (deja mesure en niveau par modele_facteur_qualite_credit.py),
pas juste son niveau actuel.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "momentum_credit"


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    if len(serie) < 2:
        raise SerieVide("pas assez de points")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant")
    return candidats[-1]


def main() -> int:
    try:
        hy = read_series(BRUT / "fred" / "BAMLH0A0HYM2.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    spread_actuel = hy[-1][1]
    date_du_jour = hy[-1][0]

    try:
        spread_12m = valeur_n_jours_avant(hy, 365)
        spread_1m = valeur_n_jours_avant(hy, 30)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    momentum_12_1 = spread_1m - spread_12m  # 12-1 mois, en points de spread (pas en %, le
                                              # spread peut etre proche de 0)
    variation_totale = spread_actuel - spread_12m

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "spread_actuel", "spread_12m_avant", "momentum_12_1_pt", "variation_12m_pt"],
        [[date_du_jour, spread_actuel, round(spread_12m, 3), round(momentum_12_1, 3),
          round(variation_totale, 3)]],
    )

    lecture = "spread qui se resserre (risque credit percu en baisse)" if momentum_12_1 < -0.1 \
        else ("spread qui s'ecarte (risque credit percu en hausse)" if momentum_12_1 > 0.1
              else "stable")
    print(f"OK -- momentum credit 12-1 mois={momentum_12_1:+.2f}pt -- {lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
