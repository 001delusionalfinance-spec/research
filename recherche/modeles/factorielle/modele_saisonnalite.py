"""Modele -- facteur saisonnier teste statistiquement (pas suppose), "Sell in May" sur S&P 500.

Teste, pas affirme : compare le rendement journalier moyen des mois "ete" (mai-octobre) vs
"hiver" (novembre-avril) avec un test t bilateral (scipy, meme fonction que dans _lib.py) --
si p >= 0.05, la difference n'est pas distinguable du bruit et ne doit PAS etre presentee comme
un effet reel.

Ecrit initialement avec seulement 2 ans d'historique (puissance statistique faible, limite
documentee a l'epoque) -- resolu le 2026-09-08 par l'extension de `ingestion_yfinance_indices.py`
a 30 ans pour `modele_stress_test_historique.py` (risque/), dont profite directement ce modele
sans rien changer ici. Toujours a lire avec prudence : meme 30 ans reste court a cote des
etudes academiques serieuses sur cet effet (Bouman & Jacobsen 2002, 100+ ans).
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs  # noqa: E402

NOM_MODELE = "saisonnalite"
MOIS_ETE = {5, 6, 7, 8, 9, 10}


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    from scipy import stats

    prix = valeurs(sp500)
    dates = [d for d, _ in sp500][1:]  # rendements[i] correspond a dates[i]
    rendements = rendements_log(prix)

    if len(rendements) < 60:
        print("echec -- moins de 60 rendements, test non pertinent")
        return 1

    rendements_ete = [r for d, r in zip(dates, rendements)
                       if date.fromisoformat(d).month in MOIS_ETE]
    rendements_hiver = [r for d, r in zip(dates, rendements)
                         if date.fromisoformat(d).month not in MOIS_ETE]

    if len(rendements_ete) < 10 or len(rendements_hiver) < 10:
        print("echec -- pas assez d'observations dans un des deux groupes")
        return 1

    t_stat, p_valeur = stats.ttest_ind(rendements_ete, rendements_hiver, equal_var=False)
    moyenne_ete = sum(rendements_ete) / len(rendements_ete) * 100
    moyenne_hiver = sum(rendements_hiver) / len(rendements_hiver) * 100
    significatif = p_valeur < 0.05

    date_du_jour = dates[-1]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_jours_ete", "n_jours_hiver", "rendement_moyen_ete_pct",
         "rendement_moyen_hiver_pct", "t_stat", "p_valeur", "significatif"],
        [[date_du_jour, len(rendements_ete), len(rendements_hiver), round(moyenne_ete, 5),
          round(moyenne_hiver, 5), round(t_stat, 3), round(p_valeur, 4), significatif]],
    )

    print(f"OK -- rendement journalier moyen ete={moyenne_ete:+.4f}%, "
          f"hiver={moyenne_hiver:+.4f}% (t={t_stat:.2f}, p={p_valeur:.4f}) -- "
          f"{'DIFFERENCE significative' if significatif else 'non significatif (attendu vu la '
          'faible puissance sur seulement ~2 ans)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
