"""Modele -- correlations croisees du positionnement speculatif (COT), 9 marches, avec test
de significativite et correction pour tests multiples.

Consomme donnees/brut/cftc/*.csv (meme source que positionnement-comportemental/
modele_positionnement_cot.py, aucune nouvelle ingestion). Correle les positions nettes
non-commerciales entre marches -- une correlation affichee sans test de significativite peut
induire en erreur des qu'on scanne plusieurs paires a la fois (C(9,2) = 36 paires ici), d'ou le
garde-fou Bonferroni.
"""

import csv
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import (BRUT, ETAT, SerieVide, accumuler_csv,  # noqa: E402
                   correlation_avec_p_valeur, seuils_bonferroni)

NOM_MODELE = "correlations_positionnement"


def lire_nets(path: Path) -> list:
    if not path.exists():
        raise SerieVide(f"{path} n'existe pas")
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return [float(l["noncomm_net"]) for l in lignes]


def main() -> int:
    dossier = BRUT / "cftc"
    fichiers = sorted(dossier.glob("*.csv")) if dossier.exists() else []
    if len(fichiers) < 2:
        print("echec -- moins de 2 marches disponibles dans donnees/brut/cftc/")
        return 1

    series = {}
    echecs = []
    for fichier in fichiers:
        try:
            series[fichier.stem] = lire_nets(fichier)
        except SerieVide as e:
            echecs.append((fichier.stem, str(e)))
            print(f"{fichier.stem} : echec -- {e}")

    paires = list(itertools.combinations(sorted(series.keys()), 2))
    if not paires:
        print("echec -- aucune paire calculable")
        return 1

    resultats = []
    p_valeurs = []
    for a, b in paires:
        try:
            r, p = correlation_avec_p_valeur(series[a], series[b])
        except SerieVide as e:
            print(f"{a}/{b} : echec -- {e}")
            continue
        resultats.append([a, b, round(r, 4), p])
        p_valeurs.append(p)

    if not resultats:
        print("echec -- aucune correlation calculable")
        return 1

    significatifs = seuils_bonferroni([p for _, _, _, p in resultats])
    date_du_jour = None
    lignes_finales = []
    for (a, b, r, p), sig in zip(resultats, significatifs):
        lignes_finales.append([a, b, r, round(p, 6), sig])
        marque = " *" if sig else ""
        print(f"{a} / {b} : r={r:+.3f}, p={p:.4f}{marque}")

    n_sig = sum(significatifs)
    print(f"\n{n_sig}/{len(resultats)} paires significatives apres correction Bonferroni "
          f"(alpha=0.05/{len(resultats)})")

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["marche_a", "marche_b", "correlation", "p_valeur", "significatif_bonferroni"],
        [[a, b, r, p, sig] for a, b, r, p, sig in lignes_finales],
    )

    if echecs:
        print(f"\n{len(echecs)} marche(s) exclue(s) : {[m for m, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
