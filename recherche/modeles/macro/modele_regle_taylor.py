"""Modele -- regle de Taylor (Taylor 1993) implicite, US, version simplifiee.

i* = r* + pi + 0.5*(pi - pi*) -- r*=2% (taux reel d'equilibre, convention Taylor 1993),
pi*=2% (cible d'inflation Fed, officielle depuis 2012). Ecart entre i* (taux "recommande" par
la regle) et le taux reel (DFF) = degre de restriction/accommodation implicite.

**Limite assumee et documentee, pas cachee** : la regle de Taylor complete a un troisieme
terme, 0.5*(y - y*) -- l'ecart de production (output gap). Aucune mesure de PIB potentiel n'est
ingeree ici -- terme omis plutot qu'approxime par un proxy invente (ex. chomage via la loi
d'Okun sans NAIRU ingeree serait une approximation d'une approximation). Version a 2 termes
seulement, explicitement signalee dans la sortie.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "regle_taylor"
TAUX_REEL_EQUILIBRE_PCT = 2.0
CIBLE_INFLATION_PCT = 2.0
POIDS_ECART_INFLATION = 0.5


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
        dff = read_series(BRUT / "fred" / "DFF.csv")
        cpi = read_series(BRUT / "fred" / "CPIAUCSL.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    try:
        cpi_an_dernier = valeur_n_jours_avant(cpi, 365)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    inflation_yoy = (cpi[-1][1] / cpi_an_dernier - 1) * 100
    taux_recommande = (TAUX_REEL_EQUILIBRE_PCT + inflation_yoy +
                        POIDS_ECART_INFLATION * (inflation_yoy - CIBLE_INFLATION_PCT))
    taux_reel_fed = dff[-1][1]
    ecart = taux_reel_fed - taux_recommande

    date_du_jour = dff[-1][0]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "inflation_yoy_pct", "taux_recommande_taylor_pct", "taux_fed_reel_pct",
         "ecart_pt", "version"],
        [[date_du_jour, round(inflation_yoy, 3), round(taux_recommande, 3),
          round(taux_reel_fed, 3), round(ecart, 3), "2_termes_sans_output_gap"]],
    )

    lecture = "restrictif (Fed au-dessus de la regle)" if ecart > 0.25 else \
        ("accommodant (Fed en-dessous de la regle)" if ecart < -0.25 else "aligne sur la regle")
    print(f"OK -- Taylor (2 termes, sans output gap)={taux_recommande:.2f}%, "
          f"Fed reel={taux_reel_fed:.2f}%, ecart={ecart:+.2f}pt -- {lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
