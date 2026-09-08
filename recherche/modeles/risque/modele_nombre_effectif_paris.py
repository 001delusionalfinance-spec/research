"""Modele -- nombre effectif de paris independants (Meucci 2010) dans le positionnement COT,
11 marches.

PCA sur la matrice de correlation des positions nettes -- si tous les marches etaient
independants, chaque composante principale expliquerait 1/11 de la variance ; s'ils sont tous
tres correles, une seule composante domine. "Nombre effectif" = exp(entropie de Shannon des
parts de variance expliquee par chaque composante) -- une mesure standard de diversification
en gestion de portefeuille (moins brutale qu'un simple compte de positions, capture le degre de
redondance). Complete modele_pca_taux.py (meme technique, univers different : positionnement,
pas taux) et modele_clustering_marches.py (regroupement qualitatif vs ce chiffre unique
quantitatif).
"""

import csv
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, correlation  # noqa: E402

NOM_MODELE = "nombre_effectif_paris"


def lire_nets(path: Path) -> list:
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return [float(l["noncomm_net"]) for l in lignes]


def main() -> int:
    import numpy as np

    dossier = BRUT / "cftc"
    fichiers = sorted(dossier.glob("*.csv")) if dossier.exists() else []
    if len(fichiers) < 3:
        print("echec -- moins de 3 marches disponibles")
        return 1

    series = {}
    for fichier in fichiers:
        try:
            series[fichier.stem] = lire_nets(fichier)
        except SerieVide as e:
            print(f"{fichier.stem} : echec -- {e}")

    marches = sorted(series.keys())
    n = len(marches)
    if n < 3:
        print("echec -- moins de 3 marches exploitables")
        return 1

    matrice_corr = np.eye(n)
    for i, j in itertools.combinations(range(n), 2):
        try:
            r = correlation(series[marches[i]], series[marches[j]])
        except SerieVide:
            r = 0.0
        matrice_corr[i, j] = r
        matrice_corr[j, i] = r

    valeurs_propres = np.linalg.eigvalsh(matrice_corr)
    valeurs_propres = np.clip(valeurs_propres, 0, None)  # bruit numerique peut donner des
                                                            # valeurs propres legerement < 0
    parts = valeurs_propres / valeurs_propres.sum()
    parts_non_nulles = parts[parts > 1e-10]
    entropie = -np.sum(parts_non_nulles * np.log(parts_non_nulles))
    nombre_effectif = float(np.exp(entropie))

    date_du_jour = None
    with fichiers[0].open(encoding="utf-8") as f:
        date_du_jour = sorted(csv.DictReader(f), key=lambda r: r["date"])[-1]["date"]

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "n_marches", "nombre_effectif_paris", "pct_du_max_possible"],
        [[date_du_jour, n, round(nombre_effectif, 2), round(nombre_effectif / n * 100, 1)]],
    )

    # lecture qualitative -- % du maximum theorique (n marches = n paris independants) :
    # >=70% diversifie, [40,70)% moderement concentre, <40% concentre (une poignee de facteurs
    # domine la variance des positions)
    pct_du_max = nombre_effectif / n * 100
    if pct_du_max >= 70:
        lecture_div = "diversifie -- peu de redondance entre les paris"
    elif pct_du_max >= 40:
        lecture_div = "moderement concentre -- redondance significative entre plusieurs paris"
    else:
        lecture_div = "concentre -- une poignee de facteurs domine, peu de paris reellement independants"

    print(f"OK -- {n} marches, nombre effectif de paris independants={nombre_effectif:.2f} "
          f"({pct_du_max:.0f}% du maximum theorique de {n}) -- {lecture_div}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
