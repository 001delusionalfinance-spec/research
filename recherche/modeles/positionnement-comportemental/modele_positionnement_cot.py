"""Modele -- positionnement speculatif extreme (z-score COT), 9 marches (actions, taux,
change, or, petrole, vol).

Z-score du positionnement net non-commercial sur une fenetre de 78 semaines (~1,5 an) --
|z| > 2 marque un positionnement extreme, lu comme un signal contrarien classique. Porte depuis
global-macro-desk-cloud, univers etendu de 4 a 9 contrats (voir ingestion_cftc.py).
"""

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, nouvelle_figure, sauvegarder_figure  # noqa: E402

NOM_MODELE = "positionnement_cot"
FENETRE_SEMAINES = 78
SEUIL_EXTREME = 2.0


def lire_cftc(path: Path) -> list:
    if not path.exists():
        raise SerieVide(f"{path} n'existe pas")
    with path.open(encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return sorted(lignes, key=lambda r: r["date"])


def zscore(valeur: float, fenetre: list) -> float:
    if len(fenetre) < 10:
        raise SerieVide("fenetre COT trop courte pour un z-score fiable")
    moyenne = sum(fenetre) / len(fenetre)
    ecart_type = math.sqrt(sum((v - moyenne) ** 2 for v in fenetre) / len(fenetre))
    if ecart_type == 0:
        raise SerieVide("ecart-type nul sur la fenetre COT")
    return (valeur - moyenne) / ecart_type


def zscore_glissant(nets: list, fenetre: int) -> list:
    out = []
    for i in range(len(nets)):
        f = nets[max(0, i - fenetre + 1):i + 1]
        if len(f) < 10:
            out.append(None)
            continue
        try:
            out.append(zscore(nets[i], f))
        except SerieVide:
            out.append(None)
    return out


def tracer(par_contrat: dict) -> None:
    styles = [("black", "-"), ("#555555", "--"), ("#888888", "-."), ("#bbbbbb", ":")]
    plt, fig, ax = nouvelle_figure(figsize=(10, 6))
    for i, (contrat, (dates, zscores)) in enumerate(par_contrat.items()):
        couleur, style = styles[i % len(styles)]
        ax.plot(dates, zscores, color=couleur, linestyle=style, linewidth=1.1, label=contrat)
    ax.axhline(SEUIL_EXTREME, color="#888888", linewidth=0.8, linestyle="--")
    ax.axhline(-SEUIL_EXTREME, color="#888888", linewidth=0.8, linestyle="--")
    ax.set_ylabel(f"Z-score positionnement net (fenetre {FENETRE_SEMAINES} sem.)")
    ax.set_xticks(ax.get_xticks()[::max(1, len(ax.get_xticks()) // 8)])
    ax.tick_params(axis="x", rotation=45)
    ax.set_title("Positionnement COT -- z-score glissant, 9 marches")
    ax.legend(fontsize=7, ncol=3)
    sauvegarder_figure(plt, fig, NOM_MODELE, "positionnement_cot")


def main() -> int:
    dossier = BRUT / "cftc"
    fichiers = sorted(dossier.glob("*.csv")) if dossier.exists() else []
    if not fichiers:
        print("echec -- aucun fichier dans donnees/brut/cftc/")
        return 1

    resultats = []
    echecs = []
    par_contrat = {}
    for fichier in fichiers:
        contrat = fichier.stem
        try:
            lignes = lire_cftc(fichier)
            nets = [float(l["noncomm_net"]) for l in lignes]
            fenetre = nets[-FENETRE_SEMAINES:]
            z = zscore(nets[-1], fenetre)
            extreme = abs(z) > SEUIL_EXTREME
            resultats.append([lignes[-1]["date"], contrat, nets[-1], round(z, 3), extreme])
            print(f"{contrat} : net={nets[-1]}, z={z:.2f}, extreme={extreme}")

            zglissant = zscore_glissant(nets, FENETRE_SEMAINES)
            dates_valides = [l["date"] for l, zg in zip(lignes, zglissant) if zg is not None]
            z_valides = [zg for zg in zglissant if zg is not None]
            if z_valides:
                par_contrat[contrat] = (dates_valides, z_valides)
        except SerieVide as e:
            echecs.append((contrat, str(e)))
            print(f"{contrat} : echec -- {e}")

    if resultats:
        accumuler_csv(ETAT / f"{NOM_MODELE}.csv",
                       ["date", "contrat", "noncomm_net", "zscore", "extreme"], resultats)
    if par_contrat:
        tracer(par_contrat)

    if echecs:
        print(f"\n{len(echecs)} contrat(s) en echec : {[c for c, _ in echecs]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
