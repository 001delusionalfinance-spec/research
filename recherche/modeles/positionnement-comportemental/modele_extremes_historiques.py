"""Modele -- proximite au positionnement net EXTREME de toute l'histoire disponible (15
marches, apres extension a RUSSELL_MINI/PALLADIUM), pas juste un z-score sur fenetre glissante.

Distinct de modele_positionnement_cot.py (z-score, fenetre 78 semaines) : ici, ou se situe le
positionnement actuel par rapport au MAX et au MIN jamais enregistres sur tout l'historique
ingere -- un z-score de +2 peut ne representer que 60% du record historique si l'historique
contient un episode encore plus extreme.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "extremes_historiques"


def lire_nets(path: Path) -> list:
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return [(l["date"], float(l["noncomm_net"])) for l in lignes]


def main() -> int:
    dossier = BRUT / "cftc"
    fichiers = sorted(dossier.glob("*.csv")) if dossier.exists() else []
    if not fichiers:
        print("echec -- aucun fichier dans donnees/brut/cftc/")
        return 1

    resultats = []
    for fichier in fichiers:
        contrat = fichier.stem
        try:
            lignes = lire_nets(fichier)
        except SerieVide as e:
            print(f"{contrat} : echec -- {e}")
            continue
        nets = [v for _, v in lignes]
        actuel = nets[-1]
        maximum, minimum = max(nets), min(nets)
        if actuel >= 0:
            pct_du_record = (actuel / maximum * 100) if maximum > 0 else 0
        else:
            pct_du_record = (actuel / minimum * 100) if minimum < 0 else 0
        resultats.append([lignes[-1][0], contrat, round(actuel, 0), round(maximum, 0),
                           round(minimum, 0), round(pct_du_record, 1)])

    if not resultats:
        print("echec -- aucun contrat exploitable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "contrat", "net_actuel", "max_historique", "min_historique",
         "pct_du_record_directionnel"],
        resultats,
    )

    plus_proche_record = max(resultats, key=lambda r: r[5])
    print(f"OK -- {len(resultats)} marches -- le plus proche de son record directionnel : "
          f"{plus_proche_record[1]} ({plus_proche_record[5]:.0f}% de son record)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
