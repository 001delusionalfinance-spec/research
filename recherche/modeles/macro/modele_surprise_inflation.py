"""Modele -- surprise d'inflation US : variation mensuelle du CPI comparee a une "prevision"
naive (moyenne des 6 variations mensuelles precedentes).

Pas une vraie surprise au sens consensus d'economistes (donnee non disponible gratuitement) --
proxy naif documente comme tel : le dernier MoM releve-t-il plus ou moins que ce qu'une simple
moyenne recente aurait suggere. Complementaire de modele_surprise_macro_composite.py (YoY,
tendance longue) -- ici sur le MoM, plus sensible aux a-coups mensuels.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "surprise_inflation"
FENETRE_PREVISION = 6


def main() -> int:
    try:
        cpi = read_series(BRUT / "fred" / "CPIAUCSL.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    niveaux = valeurs(cpi)
    if len(niveaux) < FENETRE_PREVISION + 2:
        print("echec -- historique insuffisant")
        return 1

    variations_mom = [(b / a - 1) * 100 for a, b in zip(niveaux[:-1], niveaux[1:])]
    derniere_variation = variations_mom[-1]
    prevision_naive = sum(variations_mom[-1 - FENETRE_PREVISION:-1]) / FENETRE_PREVISION
    surprise = derniere_variation - prevision_naive

    date_du_jour = cpi[-1][0]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "cpi_mom_pct", "prevision_naive_pct", "surprise_pt"],
        [[date_du_jour, round(derniere_variation, 3), round(prevision_naive, 3),
          round(surprise, 3)]],
    )

    lecture = "surprise haussiere (inflation plus forte qu'attendu)" if surprise > 0.05 else \
        ("surprise baissiere" if surprise < -0.05 else "conforme aux attentes naives")
    print(f"OK -- CPI MoM={derniere_variation:+.3f}%, prevision naive={prevision_naive:+.3f}%, "
          f"surprise={surprise:+.3f}pt -- {lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
