"""Modele -- lecture macro des matieres premieres.

Les cinq matieres premieres ingerees ne sont pas suivies pour elles-memes mais pour ce qu'elles
disent de l'economie.

- **Ratio cuivre / or** -- le cuivre sert la production industrielle, l'or sert de refuge. Leur
  rapport monte quand la croissance domine, baisse quand la peur domine. C'est l'un des rares
  indicateurs de croissance disponible en frequence quotidienne, la ou les statistiques
  officielles arrivent avec un a deux mois de retard.
- **Energie** -- Brent, WTI et gaz naturel comme intrant d'inflation. Une hausse de l'energie
  se retrouve dans les prix a la consommation quelques mois plus tard, et contraint les banques
  centrales sans qu'aucune donnee d'inflation ne soit encore parue.
- **Ecart Brent / WTI** -- son elargissement signale une contrainte logistique ou geopolitique
  sur le brut mondial plutot qu'un choc de demande.

Limite assumee : un prix de matiere premiere melange offre et demande. Une hausse du petrole
liee a une rupture d'offre et une hausse liee a une demande forte se ressemblent ici et ne
veulent pas dire la meme chose. Le ratio cuivre/or est moins expose a cette ambiguite, parce
qu'un choc d'offre sur l'un des deux metaux est rare.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "matieres_premieres_macro"
MAT = BRUT / "marches" / "matieres"
SEUIL_VARIATION_PCT = 5.0


def valeur_il_y_a(serie: list, jours: int) -> float:
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=jours)
    anterieurs = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not anterieurs:
        raise SerieVide(f"aucun point {jours} jours avant")
    return anterieurs[-1]


def variation_pct(serie: list, jours: int) -> float:
    ancien = valeur_il_y_a(serie, jours)
    if ancien == 0:
        raise SerieVide("valeur de reference nulle")
    return (serie[-1][1] / ancien - 1) * 100


def main() -> int:
    try:
        cuivre = read_series(MAT / "CUIVRE.csv", "close")
        or_ = read_series(MAT / "OR.csv", "close")
        brent = read_series(MAT / "BRENT.csv", "close")
        wti = read_series(MAT / "WTI.csv", "close")
        gaz = read_series(MAT / "GAZ_HENRY_HUB.csv", "close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    try:
        # Ratio cuivre/or aligne sur les dates communes -- indispensable, les deux contrats ne
        # cotent pas exactement les memes jours.
        index_or = dict(or_)
        communes = [(d, v / index_or[d]) for d, v in cuivre if d in index_or and index_or[d] > 0]
        if len(communes) < 300:
            raise SerieVide(f"seulement {len(communes)} dates communes cuivre/or")
        ratio_actuel = communes[-1][1]
        ratio_3m = valeur_il_y_a(communes, 91)
        var_ratio = (ratio_actuel / ratio_3m - 1) * 100

        var_brent_3m = variation_pct(brent, 91)
        var_brent_12m = variation_pct(brent, 365)
        var_gaz_3m = variation_pct(gaz, 91)
        ecart_brent_wti = brent[-1][1] - wti[-1][1]
    except (SerieVide, ZeroDivisionError) as e:
        print(f"echec -- {e}")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "ratio_cuivre_or", "variation_ratio_3m_pct", "brent_usd",
         "variation_brent_3m_pct", "variation_brent_12m_pct", "variation_gaz_3m_pct",
         "ecart_brent_wti_usd"],
        [[communes[-1][0], round(ratio_actuel, 6), round(var_ratio, 2), round(brent[-1][1], 2),
          round(var_brent_3m, 2), round(var_brent_12m, 2), round(var_gaz_3m, 2),
          round(ecart_brent_wti, 2)]],
    )

    if var_ratio > SEUIL_VARIATION_PCT:
        croissance = "le ratio cuivre/or monte -- la croissance domine la peur"
    elif var_ratio < -SEUIL_VARIATION_PCT:
        croissance = "le ratio cuivre/or baisse -- la peur domine la croissance"
    else:
        croissance = "ratio cuivre/or stable -- pas de signal net sur la croissance"

    if var_brent_12m > 15:
        inflation = ("energie nettement plus chere sur un an -- pression inflationniste a "
                     "venir que les prix a la consommation ne montrent pas encore")
    elif var_brent_12m < -15:
        inflation = "energie nettement moins chere sur un an -- effet desinflationniste en cours"
    else:
        inflation = "energie sans effet marque sur l'inflation a venir"

    print(f"OK -- {croissance} ({var_ratio:+.1f}% sur 3 mois). Brent {brent[-1][1]:.1f}$ "
          f"({var_brent_3m:+.1f}% sur 3 mois, {var_brent_12m:+.1f}% sur 12 mois), gaz "
          f"{var_gaz_3m:+.1f}% sur 3 mois, ecart Brent-WTI {ecart_brent_wti:+.1f}$ -- {inflation}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
