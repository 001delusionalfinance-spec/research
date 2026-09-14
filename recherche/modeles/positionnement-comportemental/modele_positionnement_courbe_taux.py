"""Modele -- structure du positionnement speculatif sur la courbe des taux americaine.

Lit les contrats obligataires du rapport COT (`donnees/brut/cftc/`) : 2 ans, 5 ans, 10 ans,
bond, ultra bond, ultra 10 ans, plus les contrats de taux courts (fed funds, SOFR).

**Pourquoi la structure et pas le total.** Etre short le 2 ans et long le 30 ans n'est pas la
meme vue qu'un short uniforme sur toute la courbe : le premier est un pari sur la PENTE
(anticipation de baisses de taux courts), le second sur le NIVEAU (anticipation de taux plus
hauts partout). Un chiffre agrege de positionnement obligataire melange les deux et ne dit
rien. C'est exactement le trou que le dispositif avait jusqu'au 2026-09-14, ou seul le 10 ans
etait suivi.

Chaque contrat est ramene a son **rang en percentile sur tout l'historique disponible** (~19 ans
depuis l'elargissement du 2026-09-14). Le positionnement net brut n'est pas comparable d'un
contrat a l'autre -- ils n'ont ni la meme taille ni le meme nombre d'intervenants ; le
percentile les rend comparables.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import (BRUT, ETAT, SerieVide, ecrire_csv,  # noqa: E402
                  percentile_rang, read_series)

NOM_MODELE = "positionnement_courbe_taux"
COT = BRUT / "cftc"

# Ordonnes du plus court au plus long -- l'ordre porte du sens ici, il dessine la courbe.
CONTRATS = [
    ("Fed funds", "FED_FUNDS"),
    ("SOFR 3 mois", "SOFR_3M"),
    ("2 ans", "UST_2Y"),
    ("5 ans", "UST_5Y"),
    ("10 ans", "UST_10Y"),
    ("Ultra 10 ans", "UST_ULTRA_10Y"),
    ("Bond (30 ans)", "UST_BOND"),
    ("Ultra bond", "UST_ULTRA_BOND"),
]
SEUIL_EXTREME = 85.0
SEUIL_BAS = 15.0


def main() -> int:
    lignes, echecs = [], []
    for libelle, fichier in CONTRATS:
        try:
            serie = read_series(COT / f"{fichier}.csv", "noncomm_net")
            historique = [v for _, v in serie]
            if len(historique) < 52:
                raise SerieVide(f"seulement {len(historique)} semaines d'historique")
            net = serie[-1][1]
            rang = percentile_rang(net, historique)
            sens = "long" if net > 0 else ("short" if net < 0 else "neutre")
            if rang >= SEUIL_EXTREME:
                extremite = "extreme haut"
            elif rang <= SEUIL_BAS:
                extremite = "extreme bas"
            else:
                extremite = "median"
            lignes.append((libelle, fichier, serie[-1][0], int(net), round(rang, 1),
                           len(historique), sens, extremite))
        except (SerieVide, ValueError) as e:
            echecs.append((libelle, str(e)))

    if not lignes:
        print(f"echec -- aucun contrat exploitable ({len(echecs)} en erreur)")
        return 1

    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["maturite", "contrat", "date", "position_nette_speculative",
                "percentile_historique", "n_semaines", "sens", "extremite"], lignes)

    # Lecture de structure : le positionnement des maturites courtes va-t-il dans le meme sens
    # que celui des longues ? C'est ce qui distingue un pari de pente d'un pari de niveau.
    par_libelle = {l[0]: l[6] for l in lignes}
    courtes = [par_libelle.get(m) for m in ("Fed funds", "SOFR 3 mois", "2 ans")
               if par_libelle.get(m)]
    longues = [par_libelle.get(m) for m in ("Bond (30 ans)", "Ultra bond", "Ultra 10 ans")
               if par_libelle.get(m)]
    sens_court = max(set(courtes), key=courtes.count) if courtes else None
    sens_long = max(set(longues), key=longues.count) if longues else None

    if sens_court and sens_long and sens_court != sens_long:
        lecture = (f"pari de PENTE -- les maturites courtes sont majoritairement {sens_court} "
                   f"et les longues {sens_long}, le marche joue la deformation de la courbe "
                   f"plutot que son niveau")
    elif sens_court and sens_long:
        lecture = (f"pari de NIVEAU -- courtes et longues sont {sens_court}, le marche joue un "
                   f"deplacement de toute la courbe dans le meme sens")
    else:
        lecture = "structure indeterminee"

    extremes = [f"{l[0]} ({l[7]}, {l[4]:.0f}e pct)" for l in lignes if l[7] != "median"]
    if extremes:
        lecture += f". Positionnement a un extreme historique sur : {', '.join(extremes)}"

    print(f"OK -- {len(lignes)} contrats de taux -- {lecture}")
    if echecs:
        print(f"   {len(echecs)} contrat(s) non exploitable(s) : {[n for n, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
