"""Modele -- momentum du positionnement COT lui-meme (derivee du z-score, pas son niveau).

Distinction utile : un z-score de +1,5 stable n'est pas la meme situation qu'un z-score qui
vient de passer de 0 a +1,5 en 8 semaines -- le second est un positionnement qui SE CONSTRUIT
(risque de retournement futur plus eleve si ca continue), le premier est deja stabilise. Compare
le z-score actuel au z-score d'il y a 8 semaines (~2 mois), sur l'historique brut deja ingere
par ingestion_cftc.py -- pas besoin d'attendre l'accumulation de recherche/etat/ sur plusieurs
mois comme volatilite_ewma.
"""

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "momentum_positionnement"
FENETRE_ZSCORE = 78  # meme fenetre que positionnement_cot.py -- coherence entre les deux
SEMAINES_MOMENTUM = 8


def lire_nets(path: Path) -> list:
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return [(l["date"], float(l["noncomm_net"])) for l in lignes]


def zscore(valeur: float, fenetre: list) -> float:
    if len(fenetre) < 10:
        raise SerieVide("fenetre trop courte pour un z-score fiable")
    moyenne = sum(fenetre) / len(fenetre)
    ecart_type = math.sqrt(sum((v - moyenne) ** 2 for v in fenetre) / len(fenetre))
    if ecart_type == 0:
        raise SerieVide("ecart-type nul")
    return (valeur - moyenne) / ecart_type


def zscore_a_index(nets: list, i: int, fenetre_taille: int) -> float:
    f = nets[max(0, i - fenetre_taille + 1):i + 1]
    return zscore(nets[i], f)


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
            lignes = lire_nets(fichier)
            nets = [v for _, v in lignes]
            date_du_jour = date_du_jour or lignes[-1][0]
            if len(nets) < FENETRE_ZSCORE + SEMAINES_MOMENTUM:
                raise SerieVide("historique insuffisant pour le momentum de z-score")
            z_actuel = zscore_a_index(nets, len(nets) - 1, FENETRE_ZSCORE)
            z_ancien = zscore_a_index(nets, len(nets) - 1 - SEMAINES_MOMENTUM, FENETRE_ZSCORE)
            momentum_z = z_actuel - z_ancien
        except SerieVide as e:
            echecs.append((contrat, str(e)))
            print(f"{contrat} : echec -- {e}")
            continue

        resultats.append([date_du_jour, contrat, round(z_actuel, 3), round(z_ancien, 3),
                           round(momentum_z, 3)])
        if abs(z_actuel) > abs(z_ancien):
            lecture = "se construit (l'extreme s'accroit)"
        elif abs(z_actuel) < abs(z_ancien):
            lecture = "se degonfle (l'extreme diminue)"
        else:
            lecture = "stable"
        print(f"{contrat} : z={z_actuel:+.2f} (il y a {SEMAINES_MOMENTUM}sem: {z_ancien:+.2f}), "
              f"momentum={momentum_z:+.2f} -- positionnement {lecture}")

    if not resultats:
        print("echec -- aucun contrat exploitable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "contrat", "zscore_actuel", f"zscore_il_y_a_{SEMAINES_MOMENTUM}sem",
         "momentum_zscore"],
        resultats,
    )

    if echecs:
        print(f"\n{len(echecs)} contrat(s) exclu(s) : {[c for c, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
