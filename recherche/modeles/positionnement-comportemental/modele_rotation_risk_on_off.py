"""Modele -- rotation risk-on/risk-off implicite dans le positionnement COT.

Compare le z-score moyen des actifs "risque" (SP500_EMINI, NASDAQ_MINI) a celui des actifs
"refuge" (GOLD, UST_10Y) -- si les speculateurs sont nets longs actions ET nets courts
obligations/or en meme temps, c'est une posture risk-on coherente ; l'inverse, risk-off. Un
signe MELANGE (pas de rotation coherente) est aussi une information -- pas de conviction
directionnelle claire dans le positionnement agrege. Necessite NASDAQ_MINI, ajoute a
ingestion_cftc.py le 2026-09-08 (verifie frais).
"""

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "rotation_risk_on_off"
FENETRE_ZSCORE = 78
ACTIFS_RISQUE = ["SP500_EMINI", "NASDAQ_MINI"]
ACTIFS_REFUGE = ["GOLD", "UST_10Y"]


def lire_nets(path: Path) -> list:
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return [float(l["noncomm_net"]) for l in lignes]


def zscore(valeur: float, fenetre: list) -> float:
    if len(fenetre) < 10:
        raise SerieVide("fenetre trop courte")
    moyenne = sum(fenetre) / len(fenetre)
    ecart_type = math.sqrt(sum((v - moyenne) ** 2 for v in fenetre) / len(fenetre))
    if ecart_type == 0:
        raise SerieVide("ecart-type nul")
    return (valeur - moyenne) / ecart_type


def zscore_actuel(contrat: str) -> float:
    chemin = BRUT / "cftc" / f"{contrat}.csv"
    if not chemin.exists():
        raise SerieVide(f"{chemin} n'existe pas")
    nets = lire_nets(chemin)
    return zscore(nets[-1], nets[-FENETRE_ZSCORE:])


def main() -> int:
    zscores_risque, zscores_refuge = {}, {}
    for c in ACTIFS_RISQUE:
        try:
            zscores_risque[c] = zscore_actuel(c)
        except SerieVide as e:
            print(f"{c} : echec -- {e}")
    for c in ACTIFS_REFUGE:
        try:
            zscores_refuge[c] = zscore_actuel(c)
        except SerieVide as e:
            print(f"{c} : echec -- {e}")

    if not zscores_risque or not zscores_refuge:
        print("echec -- pas assez de contrats exploitables des deux cotes")
        return 1

    moyenne_risque = sum(zscores_risque.values()) / len(zscores_risque)
    moyenne_refuge = sum(zscores_refuge.values()) / len(zscores_refuge)
    ecart = moyenne_risque - moyenne_refuge

    posture = "risk-on" if ecart > 0.5 else ("risk-off" if ecart < -0.5 else "mixte/neutre")

    date_du_jour = None
    for c in list(zscores_risque) + list(zscores_refuge):
        chemin = BRUT / "cftc" / f"{c}.csv"
        with chemin.open(encoding="utf-8") as f:
            lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
            date_du_jour = lignes[-1]["date"]
        break

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "zscore_moyen_risque", "zscore_moyen_refuge", "ecart", "posture"],
        [[date_du_jour, round(moyenne_risque, 3), round(moyenne_refuge, 3), round(ecart, 3),
          posture]],
    )

    print(f"OK -- z-score moyen risque={moyenne_risque:+.2f} ({zscores_risque}), "
          f"refuge={moyenne_refuge:+.2f} ({zscores_refuge}) -- posture={posture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
