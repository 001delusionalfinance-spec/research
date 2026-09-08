"""Modele -- crowding cross-asset : combien de marches ont un positionnement extreme
SIMULTANEMENT, pas un seul marche isole.

Seuil assoupli a 1,5 (vs 2,0 dans positionnement_cot.py) -- avec seulement 9 marches, exiger
|z|>2 sur plusieurs a la fois est rarissime par construction (rappel : |z|>2 n'arrive que ~5%
du temps par marche si la distribution etait normale -- l'intersection de plusieurs a ce seuil
serait quasi vide). Le vrai signal ici n'est pas le seuil individuel (deja couvert par
positionnement_cot.py) mais LE NOMBRE de marches simultanement tendus -- un risque systemique
de deroulement correle, pas visible en regardant un marche a la fois.
"""

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "crowding_cross_asset"
FENETRE_ZSCORE = 78
SEUIL_TENDU = 1.5


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


def main() -> int:
    dossier = BRUT / "cftc"
    fichiers = sorted(dossier.glob("*.csv")) if dossier.exists() else []
    if not fichiers:
        print("echec -- aucun fichier dans donnees/brut/cftc/")
        return 1

    zscores_du_jour = {}
    echecs = []
    date_du_jour = None
    for fichier in fichiers:
        contrat = fichier.stem
        try:
            lignes = lire_nets(fichier)
            nets = [v for _, v in lignes]
            date_du_jour = date_du_jour or lignes[-1][0]
            z = zscore(nets[-1], nets[-FENETRE_ZSCORE:])
        except SerieVide as e:
            echecs.append((contrat, str(e)))
            continue
        zscores_du_jour[contrat] = z

    if not zscores_du_jour:
        print("echec -- aucun contrat exploitable")
        return 1

    tendus = {c: z for c, z in zscores_du_jour.items() if abs(z) >= SEUIL_TENDU}
    n_tendus = len(tendus)
    n_total = len(zscores_du_jour)
    liste_tendus = ";".join(f"{c}({z:+.2f})" for c, z in sorted(tendus.items()))

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_marches_tendus", "n_marches_total", "pct_tendus", "marches_tendus"],
        [[date_du_jour, n_tendus, n_total, round(100 * n_tendus / n_total, 1), liste_tendus]],
    )

    print(f"OK -- {n_tendus}/{n_total} marches avec |z|>={SEUIL_TENDU} simultanement"
          + (f" : {liste_tendus}" if n_tendus else ""))
    if echecs:
        print(f"{len(echecs)} contrat(s) exclu(s) : {[c for c, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
