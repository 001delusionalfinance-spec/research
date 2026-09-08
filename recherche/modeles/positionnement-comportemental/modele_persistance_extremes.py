"""Modele -- persistance du positionnement extreme : depuis combien de semaines CONSECUTIVES
le z-score COT est reste au-dela d'un seuil, 13 marches.

Distinct de modele_positionnement_cot.py (l'etat actuel) et modele_momentum_positionnement.py
(la vitesse de variation) : ici, la DUREE pendant laquelle un positionnement extreme s'est
maintenu -- un z-score qui vient de franchir le seuil hier n'a pas la meme signification qu'un
qui y reste depuis 10 semaines (plus susceptible d'un retournement mecanique par epuisement des
positions disponibles a prendre dans ce sens).
"""

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "persistance_extremes"
FENETRE_ZSCORE = 78
SEUIL = 1.5


def lire_nets(path: Path) -> list:
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return [(l["date"], float(l["noncomm_net"])) for l in lignes]


def zscore(valeur: float, fenetre: list) -> float:
    if len(fenetre) < 10:
        raise SerieVide("fenetre trop courte")
    moyenne = sum(fenetre) / len(fenetre)
    ecart_type = math.sqrt(sum((v - moyenne) ** 2 for v in fenetre) / len(fenetre))
    if ecart_type == 0:
        raise SerieVide("ecart-type nul")
    return (valeur - moyenne) / ecart_type


def semaines_consecutives_extreme(nets: list, fenetre: int, seuil: float) -> int:
    """Compte en remontant depuis le dernier point tant que |z| >= seuil ET meme signe."""
    if len(nets) < fenetre + 1:
        raise SerieVide("historique insuffisant")
    zscores = []
    for i in range(fenetre, len(nets)):
        try:
            zscores.append(zscore(nets[i], nets[i - fenetre:i]))
        except SerieVide:
            zscores.append(0.0)

    if not zscores or abs(zscores[-1]) < seuil:
        return 0
    signe = zscores[-1] > 0
    compte = 0
    for z in reversed(zscores):
        if abs(z) >= seuil and (z > 0) == signe:
            compte += 1
        else:
            break
    return compte


def main() -> int:
    dossier = BRUT / "cftc"
    fichiers = sorted(dossier.glob("*.csv")) if dossier.exists() else []
    if not fichiers:
        print("echec -- aucun fichier dans donnees/brut/cftc/")
        return 1

    resultats = []
    date_du_jour = None
    for fichier in fichiers:
        contrat = fichier.stem
        try:
            lignes = lire_nets(fichier)
            date_du_jour = date_du_jour or lignes[-1][0]
            nets = [v for _, v in lignes]
            semaines = semaines_consecutives_extreme(nets, FENETRE_ZSCORE, SEUIL)
        except SerieVide as e:
            print(f"{contrat} : echec -- {e}")
            continue
        resultats.append([lignes[-1][0], contrat, semaines])
        if semaines > 0:
            print(f"{contrat} : extreme depuis {semaines} semaine(s) consecutive(s)")

    if not resultats:
        print("echec -- aucun contrat exploitable")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "contrat", "semaines_consecutives_extreme"],
        resultats,
    )
    max_persistance = max(resultats, key=lambda r: r[2])
    print(f"OK -- {len(resultats)} marches analyses, plus longue persistance : "
          f"{max_persistance[1]} ({max_persistance[2]} semaines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
