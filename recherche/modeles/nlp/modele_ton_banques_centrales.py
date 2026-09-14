"""Modele -- ton compare de la Fed, de la BCE et de la Banque d'Angleterre.

Applique **le meme lexique et la meme mesure** aux trois, et c'est tout l'interet : un score de
ton n'a aucune valeur absolue, seule sa comparaison en a. Comparer la Fed a la BCE exige donc
un instrument identique, sinon on mesure la difference entre deux lexiques et non entre deux
banques centrales.

Le lexique est importe de `modele_ton_fomc` plutot que recopie. Le dupliquer aurait garanti la
derive : deux copies divergent des qu'on enrichit l'une des deux, et la comparaison deviendrait
silencieusement fausse -- sans erreur, juste un resultat faux.

**Ce que la comparaison ne dit pas.** Les trois documents n'ont ni la meme longueur ni le meme
genre : le communique du FOMC fait quelques centaines de mots, la declaration preparee de la
BCE une dizaine de milliers, le resume de la BoE davantage encore puisqu'il inclut les minutes.
Le score etant normalise par le nombre de mots (en pour-mille), cet ecart de longueur ne le
biaise pas mecaniquement. En revanche un texte long dilue naturellement ses mots de ton, donc
un ecart de niveau entre institutions s'interprete avec prudence -- c'est le suivi de CHAQUE
institution dans le temps qui est fiable, plus que le classement entre elles a un instant donne.
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
         "variation_vs_precedent", "lecture"],
        [list(l) for l in lignes],
    )

    scores = {l[0]: l[2] for l in lignes}
    variations = {l[0]: l[4] for l in lignes if l[4] != ""}
    plus_positive = max(scores, key=scores.get)
    plus_negative = min(scores, key=scores.get)

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

    detail = ", ".join(f"{n} {s:+.2f}" for n, s in scores.items())
    print(f"OK -- ton (pour mille, meme lexique) : {detail}. Plus positive : {plus_positive}, "
          f"plus negative : {plus_negative} -- {lecture}")
    if echecs:
        print(f"   {len(echecs)} institution(s) non exploitable(s) : {[n for n, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
