"""Modele -- momentum de prix (S&P 500), definition academique classique 12-1 mois
(Jegadeesh-Titman 1993) : rendement des 12 derniers mois EN EXCLUANT le dernier mois (le
retournement court terme post-forte-hausse est un effet distinct et bien documente, pas du
momentum -- l'exclure est la definition standard, pas un choix arbitraire).

**Limite honnete, a lire avant d'etendre ce modele** : une vraie analyse factorielle
(cross-sectional) compare le momentum de PLUSIEURS actifs entre eux pour isoler le facteur --
ce modele mesure le momentum d'UN SEUL actif dans le temps (time-series momentum), premiere
brique en attendant que l'univers d'instruments s'elargisse (voir donnees/brut/, seuls SP500 et
VIX ingeres a ce jour). Les deux sont des techniques reelles et documentees dans la litterature
(time-series vs cross-sectional momentum, Moskowitz/Ooi/Pedersen 2012 pour la premiere), pas un
raccourci degrade de la seconde.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "momentum_prix"

# (nom, jours_lookback) -- 1/3/6/12 mois en jours calendaires approximatifs, et la fenetre
# 12-1 mois (lookback 360j, en excluant les ~21 derniers jours de bourse -- ~30 jours calendaires)
FENETRES = [("1_mois", 30), ("3_mois", 91), ("6_mois", 182), ("12_mois", 365)]
EXCLUSION_DERNIER_MOIS_JOURS = 30


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    if len(serie) < 2:
        raise SerieVide("pas assez de points pour comparer a n jours avant")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant la derniere date")
    return candidats[-1]


def rendement_pct(prix_debut: float, prix_fin: float) -> float:
    return (prix_fin / prix_debut - 1) * 100 if prix_debut else None


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    date_du_jour = sp500[-1][0]
    prix_actuel = sp500[-1][1]

    resultats = {}
    for nom, jours in FENETRES:
        try:
            prix_ref = valeur_n_jours_avant(sp500, jours)
            resultats[nom] = rendement_pct(prix_ref, prix_actuel)
        except SerieVide as e:
            print(f"{nom} : echec -- {e}")
            resultats[nom] = None

    try:
        prix_12m = valeur_n_jours_avant(sp500, 365)
        prix_1m = valeur_n_jours_avant(sp500, EXCLUSION_DERNIER_MOIS_JOURS)
        momentum_12_1 = rendement_pct(prix_12m, prix_1m)
    except SerieVide as e:
        print(f"momentum 12-1 : echec -- {e}")
        momentum_12_1 = None

    if all(v is None for v in list(resultats.values()) + [momentum_12_1]):
        print("echec -- aucune fenetre calculable (historique insuffisant)")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "rendement_1m_pct", "rendement_3m_pct", "rendement_6m_pct",
         "rendement_12m_pct", "momentum_12_1_pct"],
        [[date_du_jour] + [round(resultats[n], 3) if resultats[n] is not None else ""
                            for n, _ in FENETRES] +
         [round(momentum_12_1, 3) if momentum_12_1 is not None else ""]],
    )

    print(f"OK -- SP500 momentum 12-1 mois = "
          f"{round(momentum_12_1, 2) if momentum_12_1 is not None else 'indisponible'}%, "
          f"detail 1/3/6/12m = {[round(resultats[n], 2) if resultats[n] else None for n, _ in FENETRES]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
