"""Modele -- correlation glissante entre le positionnement net COT (SP500_EMINI) et le prix
S&P 500 lui-meme, sur les dates communes hebdo/quotidien alignees.

Complete modele_divergence_cot_prix.py (un instant donne) : ici, la RELATION statistique entre
prix et positionnement dans le temps -- une correlation qui s'affaiblit peut signaler que le
positionnement spéculatif suit de moins en moins le prix (les speculateurs ne "chassent" plus
la tendance de la meme facon).
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, correlation, read_series  # noqa: E402

NOM_MODELE = "correlation_cot_prix"
FENETRE_SEMAINES = 26  # ~6 mois de rapports hebdo COT
SEUIL_CORR_FORTE = 0.5  # convention standard (Cohen) : |r|>=0.5 = forte, >=0.3 = moderee
SEUIL_CORR_MODEREE = 0.3


def lire_nets(path: Path) -> list:
    with path.open(encoding="utf-8") as f:
        lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return [(l["date"], float(l["noncomm_net"])) for l in lignes]


def main() -> int:
    try:
        cot = lire_nets(BRUT / "cftc" / "SP500_EMINI.csv")
        prix = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except (SerieVide, FileNotFoundError) as e:
        print(f"echec -- {e}")
        return 1

    map_prix = dict(prix)
    dates_cot = [d for d, _ in cot]
    prix_aux_dates_cot = []
    for d in dates_cot:
        if d in map_prix:
            prix_aux_dates_cot.append(map_prix[d])
        else:
            # les dates COT (rapports hebdo, souvent vendredi) ne tombent pas toujours un jour
            # de bourse exact dans notre historique -- prend le prix disponible le plus proche
            # AVANT cette date, jamais apres (pas de fuite du futur)
            candidats = [pd for pd in map_prix if pd <= d]
            prix_aux_dates_cot.append(map_prix[max(candidats)] if candidats else None)

    paires_valides = [(n, p) for (_, n), p in zip(cot, prix_aux_dates_cot) if p is not None]
    if len(paires_valides) < FENETRE_SEMAINES + 5:
        print("echec -- pas assez de dates alignees COT/prix")
        return 1

    nets_alignes = [n for n, _ in paires_valides]
    prix_alignes = [p for _, p in paires_valides]

    try:
        corr = correlation(nets_alignes[-FENETRE_SEMAINES:], prix_alignes[-FENETRE_SEMAINES:])
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    date_du_jour = cot[-1][0]
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "correlation_cot_prix_26sem"],
        [[date_du_jour, round(corr, 4)]],
    )

    if abs(corr) >= SEUIL_CORR_FORTE:
        lecture = "forte"
    elif abs(corr) >= SEUIL_CORR_MODEREE:
        lecture = "moderee"
    else:
        lecture = "faible"
    print(f"OK -- correlation COT/prix SP500 ({FENETRE_SEMAINES} semaines) = {corr:+.3f} -- "
          f"lien {lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
