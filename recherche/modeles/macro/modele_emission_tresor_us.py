"""Modele -- offre de papier souverain americain : ou le Tresor emprunte-t-il ?

Lit le calendrier d'adjudications du Tresor (`donnees/brut/tresor_us/adjudications.csv`) et
repartit les montants offerts par segment de maturite sur les douze dernieres semaines.

**Pourquoi ca compte, et pourquoi aucun autre modele ne le voit.** L'offre de dette souveraine
pese sur les taux longs independamment de toute decision de banque centrale. Un Tresor qui
bascule son financement du court vers le long augmente la duration que le marche doit absorber
et fait monter la prime de terme -- sans que la Fed ait rien change. Un dispositif centre sur la
politique monetaire est structurellement aveugle a ce mecanisme.

Deux mesures : la repartition entre segments, et le **ratio de couverture** (bid-to-cover),
c'est-a-dire le rapport entre la demande exprimee et le montant offert. Un ratio qui se degrade
sur les maturites longues signale que le marche absorbe l'offre avec plus de difficulte, ce qui
precede generalement une hausse de la prime de terme.
"""

import csv
import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, ecrire_csv  # noqa: E402

NOM_MODELE = "emission_tresor_us"
FICHIER = BRUT / "tresor_us" / "adjudications.csv"
FENETRE_JOURS = 84   # douze semaines

# Le Tresor decrit ses titres par un type et un terme ; on les regroupe en trois segments qui
# ont chacun un effet different sur la courbe.
SEGMENTS = {"Bill": "court (moins d'un an)", "Note": "intermediaire (2 a 10 ans)",
            "Bond": "long (20 a 30 ans)"}


def main() -> int:
    if not FICHIER.exists():
        print(f"echec -- {FICHIER} n'existe pas")
        return 1

    limite = date.today() - timedelta(days=FENETRE_JOURS)
    par_segment = {}
    with FICHIER.open(encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            type_titre = (ligne.get("security_type") or "").strip()
            segment = SEGMENTS.get(type_titre)
            if segment is None:
                continue
            try:
                jour = date.fromisoformat((ligne.get("auction_date") or "")[:10])
            except ValueError:
                continue
            if jour < limite:
                continue
            try:
                montant = float(ligne.get("offering_amt") or 0)
            except ValueError:
                continue
            if montant <= 0:
                continue
            couverture = ligne.get("bid_to_cover_ratio") or ""
            entree = par_segment.setdefault(segment, {"montant": 0.0, "n": 0, "couvertures": []})
            entree["montant"] += montant
            entree["n"] += 1
            if couverture not in ("", "null"):
                try:
                    entree["couvertures"].append(float(couverture))
                except ValueError:
                    pass

    if not par_segment:
        print(f"echec -- aucune adjudication sur les {FENETRE_JOURS} derniers jours")
        return 1

    total = sum(e["montant"] for e in par_segment.values())
    lignes = []
    for segment, e in par_segment.items():
        couverture_med = (round(statistics.median(e["couvertures"]), 2)
                          if e["couvertures"] else "")
        lignes.append((segment, e["n"], round(e["montant"] / 1e9, 1),
                       round(100 * e["montant"] / total, 1), couverture_med))
    lignes.sort(key=lambda l: -l[2])

    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["segment", "n_adjudications", "montant_offert_mds_usd", "part_pct",
                "ratio_couverture_median"], lignes)

    part_long = next((l[3] for l in lignes if l[0].startswith("long")), 0.0)
    couvertures = {l[0]: l[4] for l in lignes if l[4] != ""}
    faibles = [s for s, c in couvertures.items() if c < 2.3]

    if part_long > 15:
        lecture = (f"part inhabituellement elevee de financement long ({part_long:.0f}%) -- "
                   f"davantage de duration a absorber par le marche, ce qui pousse la prime de "
                   f"terme a la hausse sans intervention de la Fed")
    else:
        lecture = (f"financement concentre sur le court et l'intermediaire, part longue a "
                   f"{part_long:.0f}% -- peu de pression par la duration")
    if faibles:
        lecture += (f". Ratio de couverture faible sur : {', '.join(faibles)} -- le marche "
                    f"absorbe cette offre avec difficulte")

    detail = ", ".join(f"{l[0]} {l[2]:.0f} Mds$ ({l[3]:.0f}%)" for l in lignes)
    print(f"OK -- {FENETRE_JOURS} derniers jours, {total / 1e9:.0f} Mds$ offerts : {detail} "
          f"-- {lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
