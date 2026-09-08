"""Modele -- "dollar smile" implicite dans le positionnement : combien le positionnement net
combine EUR/JPY/GBP s'oppose (ou pas) a celui de l'indice dollar.

En theorie, si les speculateurs sont nets courts sur les 3 devises non-USD en meme temps, c'est
coherent avec un positionnement net long USD_INDEX (memes paris, formules differentes) --
verifie ici la coherence interne plutot que de la supposer. Une divergence (positionnement
dollar fort mais devises non-USD PAS nettes courtes) signalerait un theme dollar porte par
autre chose que ces 3 devises (ex. face au CNY, non couvert ici).
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "dollar_smile"
DEVISES_NON_USD = ["EUR_FX", "JPY_FX", "GBP_FX"]


def lire_dernier_net(path: Path) -> tuple:
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return lignes[-1]["date"], float(lignes[-1]["noncomm_net"])


def main() -> int:
    nets_devises = {}
    date_du_jour = None
    for devise in DEVISES_NON_USD:
        try:
            d, net = lire_dernier_net(BRUT / "cftc" / f"{devise}.csv")
            date_du_jour = date_du_jour or d
            nets_devises[devise] = net
        except (SerieVide, FileNotFoundError) as e:
            print(f"{devise} : echec -- {e}")

    try:
        _, net_usd_index = lire_dernier_net(BRUT / "cftc" / "USD_INDEX.csv")
    except (SerieVide, FileNotFoundError) as e:
        print(f"USD_INDEX : echec -- {e}")
        return 1

    if len(nets_devises) < 2:
        print("echec -- moins de 2 devises exploitables")
        return 1

    n_devises_courtes = sum(1 for v in nets_devises.values() if v < 0)
    usd_long = net_usd_index > 0
    coherent = (usd_long and n_devises_courtes >= 2) or (not usd_long and n_devises_courtes <= 1)

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "net_usd_index", "n_devises_non_usd_courtes", "n_devises_total", "coherent"],
        [[date_du_jour, net_usd_index, n_devises_courtes, len(nets_devises), coherent]],
    )

    print(f"OK -- USD_INDEX net={net_usd_index:+.0f} ({'long' if usd_long else 'court'}), "
          f"{n_devises_courtes}/{len(nets_devises)} devises non-USD nettes courtes -- "
          f"positionnement {'coherent' if coherent else 'DIVERGENT (theme dollar pas porte par ces 3 devises)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
