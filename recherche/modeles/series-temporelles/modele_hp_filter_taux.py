"""Modele -- decomposition tendance/cycle (filtre de Hodrick-Prescott) sur le taux 10 ans US.

Separe la serie en une composante de tendance lisse et un ecart cyclique -- lambda=129600,
la constante standard pour des donnees quotidiennes (Ravn & Uhlig 2002, ajustement du lambda
mensuel/trimestriel de Hodrick-Prescott 1997 original a la frequence quotidienne, pas un
chiffre invente). L'ecart cyclique actuel (taux au-dessus/en-dessous de sa propre tendance
lissee) est une lecture differente du niveau relatif deja utilise ailleurs (tercile sur tout
l'historique, cf. modele_regime_monetaire_emploi.py) -- ici, l'ecart a une tendance LOCALE,
pas a l'historique entier.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "hp_filter_taux"
LAMBDA_QUOTIDIEN = 129600  # Ravn & Uhlig 2002, ajustement quotidien du HP standard


def main() -> int:
    try:
        dgs10 = read_series(BRUT / "fred" / "DGS10.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    niveaux = valeurs(dgs10)
    date_du_jour = dgs10[-1][0]
    if len(niveaux) < 100:
        print("echec -- moins de 100 points, HP filter non fiable")
        return 1

    from statsmodels.tsa.filters.hp_filter import hpfilter

    cycle, tendance = hpfilter(niveaux, lamb=LAMBDA_QUOTIDIEN)
    cycle_actuel = float(cycle[-1])
    tendance_actuelle = float(tendance[-1])
    taux_observe = niveaux[-1]

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "taux_10ans_observe", "tendance_hp", "cycle_hp"],
        [[date_du_jour, taux_observe, round(tendance_actuelle, 4), round(cycle_actuel, 4)]],
    )

    lecture = "au-dessus de sa tendance locale" if cycle_actuel > 0.1 else \
        ("en-dessous de sa tendance locale" if cycle_actuel < -0.1 else "proche de sa tendance")
    print(f"OK -- taux 10 ans observe={taux_observe:.3f}%, tendance HP={tendance_actuelle:.3f}%, "
          f"ecart cyclique={cycle_actuel:+.3f}pt -- {lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
