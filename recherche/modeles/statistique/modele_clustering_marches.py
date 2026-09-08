"""Modele -- clustering hierarchique des 11 marches COT par distance de correlation.

Distance = 1 - |correlation| (deux marches tres correles, positif ou negatif, sont "proches" --
le signe importe moins que la force du lien pour la question "est-ce que je double un pari sans
le savoir"). Linkage moyen (average linkage), scipy (deja une dependance via arch/statsmodels).
Complete correlations_positionnement.py (36 paires listees a plat) en regroupant directement
les marches qui bougent ensemble.
"""

import csv
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, correlation  # noqa: E402

NOM_MODELE = "clustering_marches"
N_CLUSTERS = 4


def lire_nets(path: Path) -> list:
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return [float(l["noncomm_net"]) for l in lignes]


def main() -> int:
    import numpy as np
    from scipy.cluster.hierarchy import fcluster, linkage

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

    matrice_distance = np.zeros((n, n))
    for i, j in itertools.combinations(range(n), 2):
        try:
            r = correlation(series[marches[i]], series[marches[j]])
        except SerieVide:
            r = 0.0
        d = 1 - abs(r)
        matrice_distance[i, j] = d
        matrice_distance[j, i] = d

    from scipy.spatial.distance import squareform
    condensee = squareform(matrice_distance, checks=False)
    Z = linkage(condensee, method="average")
    clusters = fcluster(Z, t=N_CLUSTERS, criterion="maxclust")

    groupes = {}
    for marche, cluster_id in zip(marches, clusters):
        groupes.setdefault(int(cluster_id), []).append(marche)

    date_du_jour = None
    with fichiers[0].open(encoding="utf-8") as f:
        date_du_jour = sorted(csv.DictReader(f), key=lambda r: r["date"])[-1]["date"]

    lignes_csv = [[date_du_jour, marche, int(cid)] for marche, cid in zip(marches, clusters)]
    accumuler_csv(ETAT / f"{NOM_MODELE}.csv", ["date", "marche", "cluster"], lignes_csv)

    print(f"OK -- {n} marches, {len(groupes)} clusters (average linkage, distance=1-|r|) :")
    for cid, membres in sorted(groupes.items()):
        print(f"  cluster {cid} : {membres}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
