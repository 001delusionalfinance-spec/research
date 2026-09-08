"""Modele -- cycle immobilier US : mises en chantier, permis de construire, taux hypothecaire
30 ans.

Les permis PRECEDENT les mises en chantier dans le processus de construction reel (on demande
un permis avant de construire) -- compare leur tendance 6 mois : si les permis ralentissent
avant les mises en chantier, c'est un signal avance du cycle, pas juste un constat du present.
Taux hypothecaire ajoute comme contexte (le cout du financement, driver connu de la demande).
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "cycle_immobilier"


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    if len(serie) < 2:
        raise SerieVide("pas assez de points")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant")
    return candidats[-1]


def tendance_6m(serie: list) -> str:
    ref = valeur_n_jours_avant(serie, 182)
    actuel = serie[-1][1]
    ecart = (actuel - ref) / abs(ref) if ref else 0
    if ecart > 0.03:
        return "hausse"
    if ecart < -0.03:
        return "baisse"
    return "stable"


def main() -> int:
    try:
        houst = read_series(BRUT / "fred" / "HOUST.csv")
        permit = read_series(BRUT / "fred" / "PERMIT.csv")
        mortgage = read_series(BRUT / "fred" / "MORTGAGE30US.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    try:
        tendance_houst = tendance_6m(houst)
        tendance_permit = tendance_6m(permit)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    divergence = tendance_permit == "baisse" and tendance_houst != "baisse"
    date_du_jour = houst[-1][0]

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "mises_en_chantier", "tendance_chantier", "permis", "tendance_permis",
         "taux_hypothecaire_30ans", "divergence_permis_avant_chantier"],
        [[date_du_jour, houst[-1][1], tendance_houst, permit[-1][1], tendance_permit,
          mortgage[-1][1], divergence]],
    )

    print(f"OK -- mises en chantier={houst[-1][1]}k ({tendance_houst}), "
          f"permis={permit[-1][1]}k ({tendance_permit}), taux hypothecaire="
          f"{mortgage[-1][1]:.2f}% -- {'DIVERGENCE (permis ralentissent avant les chantiers)' if divergence else 'pas de divergence'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
