"""Modele -- clustering non supervise (k-means, k=3) des regimes de marche, sur 3 dimensions :
niveau VIX, spread de courbe (10-2 ans), taux directeur US.

Contrairement aux modeles a seuils fixes (comme
modele_conditions_financieres.py) qui DEFINISSENT les regimes a l'avance, k-means les
DECOUVRE a partir des donnees -- peut reveler des regroupements non intuitifs. Implementation a
la main (Lloyd standard, pas sklearn -- 3 dimensions, k=3, pas besoin d'une librairie ML),
validee sur cas synthetique a 3 clusters bien separes avant le test reel.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "kmeans_regimes"
K = 3
GRAINE = 42
MAX_ITERATIONS = 100


def kmeans(points: list, k: int, graine: int = GRAINE) -> tuple:
    """Retourne (assignations, centres) -- Lloyd standard, initialisation k-means++."""
    rng = random.Random(graine)
    n = len(points)
    if n < k * 5:
        raise SerieVide(f"moins de {k * 5} points -- k-means non fiable pour k={k}")

    centres = [list(points[rng.randrange(n)])]
    for _ in range(k - 1):
        distances = [min(sum((p[d] - c[d]) ** 2 for d in range(len(p))) for c in centres)
                     for p in points]
        total = sum(distances)
        if total == 0:
            centres.append(list(points[rng.randrange(n)]))
            continue
        seuil = rng.uniform(0, total)
        cumul = 0.0
        for p, d in zip(points, distances):
            cumul += d
            if cumul >= seuil:
                centres.append(list(p))
                break

    assignations = [0] * n
    for _ in range(MAX_ITERATIONS):
        nouvelles_assignations = []
        for p in points:
            distances = [sum((p[d] - c[d]) ** 2 for d in range(len(p))) for c in centres]
            nouvelles_assignations.append(distances.index(min(distances)))
        if nouvelles_assignations == assignations:
            break
        assignations = nouvelles_assignations
        for ci in range(k):
            membres = [p for p, a in zip(points, assignations) if a == ci]
            if membres:
                centres[ci] = [sum(p[d] for p in membres) / len(membres)
                                for d in range(len(points[0]))]
    return assignations, centres


def standardiser(colonnes: list) -> list:
    """Standardise chaque dimension (moyenne 0, ecart-type 1) -- necessaire, sinon le taux
    directeur (echelle ~0-5) domine artificiellement le VIX (echelle ~10-80) dans la distance."""
    n_dims = len(colonnes)
    n_points = len(colonnes[0])
    stats = []
    for col in colonnes:
        m = sum(col) / len(col)
        s = (sum((x - m) ** 2 for x in col) / len(col)) ** 0.5
        stats.append((m, s if s > 0 else 1.0))
    return [[(colonnes[d][i] - stats[d][0]) / stats[d][1] for d in range(n_dims)]
            for i in range(n_points)]


def main() -> int:
    try:
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
        dgs10 = read_series(BRUT / "fred" / "DGS10.csv")
        dgs2 = read_series(BRUT / "fred" / "DGS2.csv")
        dff = read_series(BRUT / "fred" / "DFF.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in vix) & set(d for d, _ in dgs10) &
                             set(d for d, _ in dgs2) & set(d for d, _ in dff))
    if len(dates_communes) < K * 5:
        print(f"echec -- {len(dates_communes)} dates communes, moins de {K * 5}")
        return 1

    map_vix, map10, map2, map_dff = dict(vix), dict(dgs10), dict(dgs2), dict(dff)
    col_vix = [map_vix[d] for d in dates_communes]
    col_spread = [map10[d] - map2[d] for d in dates_communes]
    col_taux = [map_dff[d] for d in dates_communes]

    points_standardises = standardiser([col_vix, col_spread, col_taux])

    try:
        assignations, centres = kmeans(points_standardises, K)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    cluster_actuel = assignations[-1]
    date_du_jour = dates_communes[-1]
    taille_clusters = {c: assignations.count(c) for c in range(K)}

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "vix", "spread_courbe", "taux_directeur", "cluster_actuel",
         "taille_clusters"],
        [[date_du_jour, col_vix[-1], round(col_spread[-1], 3), col_taux[-1], cluster_actuel,
          str(taille_clusters)]],
    )

    # Label economique derive du centre du cluster assigne sur la dimension VIX (standardisee,
    # donc 0 = moyenne historique) -- pas un nouveau chiffre, juste une lecture du centre deja
    # calcule par kmeans().
    vix_centre_cluster = centres[cluster_actuel][0]
    if vix_centre_cluster > 0.3:
        label_regime = "regime tendu (VIX du cluster au-dessus de la moyenne historique)"
    elif vix_centre_cluster < -0.3:
        label_regime = "regime calme (VIX du cluster en-dessous de la moyenne historique)"
    else:
        label_regime = "regime intermediaire (VIX du cluster proche de la moyenne historique)"

    print(f"OK -- {len(dates_communes)} points, k={K} -- point actuel (VIX={col_vix[-1]:.1f}, "
          f"spread={col_spread[-1]:+.2f}, taux={col_taux[-1]:.2f}%) -> cluster {cluster_actuel} "
          f"(tailles : {taille_clusters}) -- {label_regime}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
