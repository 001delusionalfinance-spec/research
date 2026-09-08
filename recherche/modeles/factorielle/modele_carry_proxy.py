"""Modele -- proxy de carry cross-asset : differentiel de taux directeur entre chaque bloc et
les US.

Le carry trade classique (emprunter dans une devise a taux bas, placer dans une devise a taux
haut) rapporte en premiere approximation le differentiel de taux, avant effet de change --
approxime ici par le differentiel de taux seul (pas encore le rendement total carry, qui
demanderait le prix spot de la devise pour mesurer l'effet de change, non ingere pour
EUR/GBP/JPY/CNY a ce jour, seul leur POSITIONNEMENT COT l'est). Limite assumee et documentee,
pas cachee -- un vrai carry return sera calculable des que des prix spot FX rejoignent
donnees/brut/.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "carry_proxy"

BLOCS = {
    "Zone_euro": "ECBDFR",
    "Royaume-Uni": "IUDSOIA",
    "Japon": "IRSTCI01JPM156N",
    "Chine": "IR3TIB01CNM156N",
}
SERIE_US = "DFF"


def main() -> int:
    try:
        us = read_series(BRUT / "fred" / f"{SERIE_US}.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    taux_us = us[-1][1]
    date_du_jour = us[-1][0]

    resultats = []
    for bloc, series_id in BLOCS.items():
        try:
            serie = read_series(BRUT / "fred" / f"{series_id}.csv")
        except SerieVide as e:
            print(f"{bloc} : echec -- {e}")
            continue
        taux_bloc = serie[-1][1]
        differentiel = taux_bloc - taux_us
        resultats.append([date_du_jour, bloc, taux_bloc, taux_us, round(differentiel, 3)])
        signe = "carry positif (taux > US)" if differentiel > 0 else "carry negatif (taux < US)"
        print(f"{bloc} : {taux_bloc:.2f}% vs US {taux_us:.2f}% -- diff={differentiel:+.2f}pt "
              f"({signe})")

    if not resultats:
        print("echec -- aucun bloc exploitable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "bloc", "taux_bloc", "taux_us", "differentiel_pt"],
        resultats,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
