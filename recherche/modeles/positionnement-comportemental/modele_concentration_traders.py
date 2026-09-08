"""Modele -- concentration du positionnement speculatif, proxy par position moyenne par trader.

**Limite assumee des le depart, pas decouverte apres coup** : un vrai indice de concentration
(Herfindahl) demande la position de CHAQUE trader individuellement -- le rapport COT legacy ne
publie que des agregats (position nette totale, nombre de traders). Proxy retenu : position
nette moyenne par trader (|position nette| / nombre de traders non-commerciaux) -- une hausse
signale moins de traders portant une exposition plus grosse chacun (concentration qui augmente),
sans etre le vrai indice Herfindahl. Necessite les colonnes traders_* ajoutees a
ingestion_cftc.py (2026-09-08).
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "concentration_traders"


def lire_derniere_ligne(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    if "traders_total" not in lignes[-1]:
        raise SerieVide(f"{path} ne contient pas traders_total -- ingestion_cftc.py pas a "
                         f"jour (colonnes ajoutees le 2026-09-08)")
    return lignes[-1]


def main() -> int:
    dossier = BRUT / "cftc"
    fichiers = sorted(dossier.glob("*.csv")) if dossier.exists() else []
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
            traders_total = int(derniere["traders_total"])
        except SerieVide as e:
            echecs.append((contrat, str(e)))
            print(f"{contrat} : echec -- {e}")
            continue

        date_du_jour = date_du_jour or derniere["date"]
        if traders_total == 0:
            print(f"{contrat} : ignore -- 0 trader rapporte")
            continue
        position_moyenne = abs(noncomm_net) / traders_total
        resultats.append([derniere["date"], contrat, traders_total, round(position_moyenne, 1)])
        print(f"{contrat} : {traders_total} traders, position nette moyenne/trader="
              f"{position_moyenne:.0f}")

    if not resultats:
        print("echec -- aucun contrat exploitable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "contrat", "traders_total", "position_moyenne_par_trader"],
        resultats,
    )
    if echecs:
        print(f"\n{len(echecs)} contrat(s) exclu(s) : {[c for c, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
