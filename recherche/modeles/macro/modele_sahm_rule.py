"""Modele -- regle de Sahm (Claudia Sahm, Fed), indicateur de recession US.

Declenchee quand la moyenne mobile 3 mois du taux de chomage national monte de 0,50 point de
pourcentage ou plus par rapport a son plus bas sur les 12 derniers mois. Regle simple, publique,
suivie de facon informelle par la Fed elle-meme (a inspire un "Sahm Rule real-time indicator"
officiel sur FRED, mais recalculee ici directement depuis UNRATE deja ingere -- pas dependante
d'une deuxieme serie a ajouter).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "sahm_rule"
SEUIL_DECLENCHEMENT_PT = 0.50


def moyenne_mobile_3m(valeurs_mensuelles: list) -> list:
    """Moyenne mobile 3 points -- les 2 premiers points de sortie sont absents (amorçage)."""
    if len(valeurs_mensuelles) < 3:
        raise SerieVide("moins de 3 points -- moyenne mobile 3 mois impossible")
    return [sum(valeurs_mensuelles[i - 2:i + 1]) / 3 for i in range(2, len(valeurs_mensuelles))]


def main() -> int:
    try:
        unrate = read_series(BRUT / "fred" / "UNRATE.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    valeurs_chomage = valeurs(unrate)
    try:
        mm3 = moyenne_mobile_3m(valeurs_chomage)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    if len(mm3) < 12:
        print("echec -- moins de 12 points de moyenne mobile -- fenetre 12 mois incomplete")
        return 1

    fenetre_12m = mm3[-12:]
    plus_bas_12m = min(fenetre_12m)
    mm3_actuelle = mm3[-1]
    ecart = mm3_actuelle - plus_bas_12m
    declenchee = ecart >= SEUIL_DECLENCHEMENT_PT

    date_du_jour = unrate[-1][0]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "unrate_dernier", "mm3_chomage", "plus_bas_mm3_12m", "ecart_pt",
         "regle_declenchee"],
        [[date_du_jour, valeurs_chomage[-1], round(mm3_actuelle, 3), round(plus_bas_12m, 3),
          round(ecart, 3), declenchee]],
    )

    print(f"OK -- MM3 chomage={mm3_actuelle:.2f}%, plus bas 12m={plus_bas_12m:.2f}%, "
          f"ecart={ecart:.2f}pt (seuil {SEUIL_DECLENCHEMENT_PT}pt) -- "
          f"{'DECLENCHEE' if declenchee else 'non declenchee'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
