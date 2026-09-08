"""Modele -- indice de surprise macro composite US (esprit Citi Economic Surprise Index,
simplifie -- 3 series, pas le panier complet proprietaire de Citi).

Pas une vraie "surprise" au sens Bloomberg/Citi (ecart au consensus des economistes, donnee
propriétaire non disponible ici) -- proxy : ecart du dernier print a sa propre tendance
recente (12 mois), sur 3 series deja ingerees (chomage, credit bancaire, inflation), chacune
signee pour que positif = surprise economique FAVORABLE (chomage qui baisse plus vite que sa
tendance = bonne surprise, d'ou le signe invers pour UNRATE).
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "surprise_macro_composite"

# (nom, fichier, signe -- +1 si "monte plus vite que tendance" = bonne surprise, -1 si l'inverse)
SERIES = [
    ("chomage", "UNRATE", -1),
    ("credit_bancaire", "TOTBKCR", 1),
    ("inflation", "CPIAUCSL", -1),  # inflation qui accelere plus que tendance = mauvaise surprise
]


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    if len(serie) < 2:
        raise SerieVide("pas assez de points")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant")
    return candidats[-1]


def main() -> int:
    surprises = {}
    date_du_jour = None
    for nom, fichier, signe in SERIES:
        try:
            serie = read_series(BRUT / "fred" / f"{fichier}.csv")
            date_du_jour = date_du_jour or serie[-1][0]
            reference_6m = valeur_n_jours_avant(serie, 182)
            reference_12m = valeur_n_jours_avant(serie, 365)
        except SerieVide as e:
            print(f"{nom} : echec -- {e}")
            continue
        # "surprise" = tendance recente (6m) qui accelere par rapport a la tendance longue (12m)
        tendance_recente = serie[-1][1] - reference_6m
        tendance_longue = reference_6m - reference_12m
        acceleration = tendance_recente - tendance_longue
        surprises[nom] = signe * acceleration

    if len(surprises) < 2:
        print("echec -- moins de 2 series exploitables")
        return 1

    # normalise chaque composante par sa propre echelle (evite que TOTBKCR, en milliards,
    # domine numeriquement UNRATE, en points de pourcentage) -- signe seul agrege, pas la valeur
    signes_surprises = {k: (1 if v > 0 else (-1 if v < 0 else 0)) for k, v in surprises.items()}
    indice = sum(signes_surprises.values()) / len(signes_surprises)

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "indice_surprise", "n_composantes"] + list(surprises.keys()),
        [[date_du_jour, round(indice, 3), len(surprises)] +
         [round(v, 4) for v in surprises.values()]],
    )

    lecture = "positif (surprises favorables dominent)" if indice > 0.2 else \
        ("negatif (surprises defavorables dominent)" if indice < -0.2 else "mixte")
    print(f"OK -- indice de surprise macro={indice:+.2f} ({signes_surprises}) -- {lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
