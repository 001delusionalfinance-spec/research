"""Modele -- ratio commercial/non-commercial (COT), proxy hedgers vs speculateurs, tous les contrats presents dans donnees/brut/cftc/.

Les "commercial" du rapport COT sont en theorie des acteurs qui couvrent une exposition reelle
(producteurs, importateurs, teneurs de marche) -- leur positionnement net est structurellement
souvent l'inverse des speculateurs (qui prennent le risque que les commerciaux couvrent).
Ratio = |position nette commerciale| / |position nette speculative| -- un ratio qui s'ecarte
de sa norme historique peut signaler un desequilibre entre couverture reelle et paris directionnels.
Necessite les colonnes comm_long/comm_short ajoutees a ingestion_cftc.py (2026-09-08).


NOTE DE PERIMETRE (2026-09-14) : ce modele PARCOURT le dossier des donnees COT, il ne
travaille donc pas sur une liste figee. L'univers est passe de 9 a 32 contrats le 2026-09-14
et les sorties d'avant cette date ne sont pas comparables a celles d'apres.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "ratio_commercial_speculatif"


def lire_derniere_ligne(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    if "comm_net" not in lignes[-1]:
        raise SerieVide(f"{path} ne contient pas comm_net -- ingestion_cftc.py pas a jour "
                         f"(colonnes ajoutees le 2026-09-08, refaire une ingestion)")
    return lignes[-1]


def main() -> int:
    dossier = BRUT / "cftc"
    fichiers = sorted(p for p in dossier.glob("*.csv")) if dossier.exists() else []
    if not fichiers:
        print("echec -- aucun fichier dans donnees/brut/cftc/")
        return 1

    resultats = []
    echecs = []
    date_du_jour = None
    for fichier in fichiers:
        contrat = fichier.stem
        try:
            derniere = lire_derniere_ligne(fichier)
            noncomm_net = float(derniere["noncomm_net"])
            comm_net = float(derniere["comm_net"])
        except SerieVide as e:
            echecs.append((contrat, str(e)))
            print(f"{contrat} : echec -- {e}")
            continue

        date_du_jour = date_du_jour or derniere["date"]
        if noncomm_net == 0:
            print(f"{contrat} : ignore -- position speculative nette nulle, ratio non defini")
            continue
        ratio = abs(comm_net) / abs(noncomm_net)
        sens_oppose = (comm_net > 0) != (noncomm_net > 0)
        resultats.append([derniere["date"], contrat, comm_net, noncomm_net, round(ratio, 3),
                           sens_oppose])
        print(f"{contrat} : commercial={comm_net:+.0f}, speculatif={noncomm_net:+.0f}, "
              f"ratio={ratio:.2f}, sens_oppose={sens_oppose}")

    if not resultats:
        print("echec -- aucun contrat exploitable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "contrat", "comm_net", "noncomm_net", "ratio_abs", "sens_oppose"],
        resultats,
    )
    if echecs:
        print(f"\n{len(echecs)} contrat(s) exclu(s) : {[c for c, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
