"""Modele -- ton compare de la Fed, de la BCE et de la Banque d'Angleterre.

Applique **le meme lexique et la meme mesure** aux trois, et c'est tout l'interet : un score de
ton n'a aucune valeur absolue, seule sa comparaison en a. Comparer la Fed a la BCE exige donc
un instrument identique, sinon on mesure la difference entre deux lexiques et non entre deux
banques centrales.

Le lexique est importe de `modele_ton_fomc` plutot que recopie. Le dupliquer aurait garanti la
derive : deux copies divergent des qu'on enrichit l'une des deux, et la comparaison deviendrait
silencieusement fausse -- sans erreur, juste un resultat faux.

**Le classement entre institutions n'est PAS publie, et ce n'est pas un oubli.**

Une premiere version affichait "plus positive : Fed, plus negative : BoE". Un audit le meme
jour a montre que ce classement etait du bruit. La raison est arithmetique : le score est
normalise par le nombre de mots, or les trois documents n'ont pas du tout la meme taille --
le communique du FOMC fait environ 150 mots, la declaration preparee de la BCE environ 1 800,
le resume de la BoE environ 3 900 puisqu'il inclut les minutes. UN SEUL mot de ton deplace
donc le score de :

    Fed  : 6,7 pour mille        BCE : 0,6 pour mille        BoE : 0,3 pour mille

soit un facteur 26 entre la Fed et la BoE. L'ecart Fed/BCE observe ce jour-la (6,1) valait
donc MOINS D'UN MOT cote Fed. Classer trois institutions sur une grandeur dont la resolution
varie d'un facteur 26 entre elles ne mesure que la longueur de leurs documents.

Ce qui reste valide, et que le modele publie : le suivi de CHAQUE institution dans le temps.
La comparaison d'un document au precedent de la MEME institution porte sur des textes de
longueur voisine, donc la variation a un sens. La sensibilite par mot est ecrite dans la sortie
pour que personne ne recompare les institutions entre elles sans le savoir.
"""

import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parents[0]))
sys.path.insert(0, str(ICI))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402
from modele_ton_fomc import score_ton  # noqa: E402  -- meme instrument pour les trois

NOM_MODELE = "ton_banques_centrales"

# (institution, dossier, motif de fichier)
SOURCES = [
    ("Fed", BRUT / "fomc", "[0-9]*.txt"),   # nommes par date brute (20260617.txt), pas prefixes
    ("BCE", BRUT / "bce", "declaration_*.txt"),
    ("Banque d'Angleterre", BRUT / "boe", "resume_*.txt"),
]
SEUIL_VARIATION = 0.5   # en pour-mille, ecart en deca duquel le ton est juge inchange


def dernier_et_precedent(dossier: Path, motif: str) -> list:
    fichiers = sorted(dossier.glob(motif))
    if not fichiers:
        raise SerieVide(f"aucun fichier {motif} dans {dossier}")
    return fichiers[-2:]


def main() -> int:
    lignes, echecs = [], []
    for institution, dossier, motif in SOURCES:
        try:
            fichiers = dernier_et_precedent(dossier, motif)
            mesures = []
            for chemin in fichiers:
                score, n_mots = score_ton(chemin.read_text(encoding="utf-8"))
                mesures.append((chemin.stem, round(score, 3), n_mots))
            actuel = mesures[-1]
            if len(mesures) == 2:
                variation = actuel[1] - mesures[0][1]
                if variation > SEUIL_VARIATION:
                    sens = "ton plus positif que la publication precedente"
                elif variation < -SEUIL_VARIATION:
                    sens = "ton plus negatif que la publication precedente"
                else:
                    sens = "ton inchange"
            else:
                variation, sens = "", "une seule publication ingeree, pas de comparaison"
            lignes.append((institution, actuel[0], actuel[1], actuel[2],
                           round(variation, 3) if variation != "" else "", sens))
        except (SerieVide, OSError) as e:
            echecs.append((institution, str(e)))

    if not lignes:
        print(f"echec -- aucune institution exploitable ({len(echecs)} en erreur)")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["institution", "document", "score_ton_pour_mille", "n_mots",
         "variation_vs_precedent", "lecture", "sensibilite_un_mot_pour_mille"],
        [list(l) + [round(1000 / l[3], 2) if l[3] else ""] for l in lignes],
    )

    scores = {l[0]: l[2] for l in lignes}
    variations = {l[0]: l[4] for l in lignes if l[4] != ""}

    if variations:
        montent = [n for n, v in variations.items() if v > SEUIL_VARIATION]
        descendent = [n for n, v in variations.items() if v < -SEUIL_VARIATION]
        if montent and descendent:
            lecture = (f"les tons DIVERGENT -- {', '.join(montent)} se detend pendant que "
                       f"{', '.join(descendent)} se durcit")
        elif descendent:
            lecture = f"durcissement du ton chez {', '.join(descendent)}"
        elif montent:
            lecture = f"detente du ton chez {', '.join(montent)}"
        else:
            lecture = "aucun changement de ton notable depuis la publication precedente"
    else:
        lecture = "pas assez d'historique pour comparer"

    # On affiche la VARIATION de chaque institution, pas son niveau compare aux autres.
    detail = ", ".join(
        f"{l[0]} {l[4]:+.2f}" if l[4] != "" else f"{l[0]} (pas d'anterieur)" for l in lignes)
    sensibilite = ", ".join(f"{l[0]} {1000 / l[3]:.1f}" for l in lignes if l[3])
    print(f"OK -- variation du ton depuis la publication precedente, par institution "
          f"(pour mille, meme lexique) : {detail} -- {lecture}. "
          f"Les niveaux ne sont PAS comparables entre institutions : un seul mot de ton les "
          f"deplace de {sensibilite} pour mille respectivement, selon la longueur du document")
    if echecs:
        print(f"   {len(echecs)} institution(s) non exploitable(s) : {[n for n, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
