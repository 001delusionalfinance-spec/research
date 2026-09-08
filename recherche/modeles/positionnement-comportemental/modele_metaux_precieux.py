"""Modele -- positionnement compare sur les 3 metaux precieux/industriels suivis (GOLD, SILVER,
PLATINUM), z-scores cote a cote.

L'or est majoritairement un actif refuge/monetaire, l'argent et le platine ont une composante
industrielle plus forte (electronique, catalyseurs automobiles) -- un positionnement qui diverge
entre l'or et les deux autres peut signaler un theme "refuge" pur plutot qu'un theme
"matieres premieres industrielles" plus large. Necessite SILVER/PLATINUM, ajoutes a
ingestion_cftc.py (2026-09-08, verifies frais).
"""

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "metaux_precieux"
FENETRE_ZSCORE = 78
METAUX = ["GOLD", "SILVER", "PLATINUM"]
SEUIL_EXTREME = 2.0  # meme seuil que modele_positionnement_cot.py -- |z| > 2 = extreme


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


def main() -> int:
    resultats = {}
    date_du_jour = None
    for metal in METAUX:
        chemin = BRUT / "cftc" / f"{metal}.csv"
        try:
            lignes = lire_nets(chemin)
            date_du_jour = date_du_jour or lignes[-1][0]
            nets = [v for _, v in lignes]
            z = zscore(nets[-1], nets[-FENETRE_ZSCORE:])
        except (SerieVide, FileNotFoundError) as e:
            print(f"{metal} : echec -- {e}")
            continue
        resultats[metal] = z

    if len(resultats) < 2:
        print("echec -- moins de 2 metaux exploitables")
        return 1

    ecart_or_vs_industriels = None
    if "GOLD" in resultats and len(resultats) > 1:
        autres = [v for k, v in resultats.items() if k != "GOLD"]
        if autres:
            ecart_or_vs_industriels = resultats["GOLD"] - sum(autres) / len(autres)

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date"] + list(resultats.keys()) + ["ecart_or_vs_industriels"],
        [[date_du_jour] + [round(v, 3) for v in resultats.values()] +
         [round(ecart_or_vs_industriels, 3) if ecart_or_vs_industriels is not None else ""]],
    )

    metal_extreme, z_extreme = max(resultats.items(), key=lambda kv: abs(kv[1]))
    if abs(z_extreme) > SEUIL_EXTREME:
        lecture_extreme = f"{metal_extreme} ressort en extreme (|z|>{SEUIL_EXTREME:.0f})"
    else:
        lecture_extreme = f"{metal_extreme} le plus tendu, sans franchir le seuil extreme (|z|>{SEUIL_EXTREME:.0f})"

    if ecart_or_vs_industriels is not None:
        print(f"OK -- z-scores : {resultats} -- {lecture_extreme} -- "
              f"ecart or/industriels={ecart_or_vs_industriels:+.2f}")
    else:
        print(f"OK -- z-scores : {resultats} -- {lecture_extreme}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
