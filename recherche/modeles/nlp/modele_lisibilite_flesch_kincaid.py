"""Modele -- indice de lisibilite Flesch-Kincaid (Reading Ease + Grade Level), communique ET
minutes FOMC -- remplace le proxy "part de mots longs >6 lettres" de complexite_texte_fomc.py
par un indice academique reconnu (Flesch 1948, Kincaid 1975), formule standard.

Comptage de syllabes heuristique (groupes de voyelles, pas un dictionnaire phonetique complet
type CMUdict -- approximation standard largement utilisee en l'absence de dictionnaire, precise
a ~90% sur l'anglais courant d'apres la litterature du domaine, documentee comme approximation).

Reading Ease = 206.835 - 1.015*(mots/phrases) - 84.6*(syllabes/mots) -- plus haut = plus facile
a lire (90-100 = tres facile, 0-30 = tres difficile, langage juridique/academique typiquement
dans les 30). Grade Level = 0.39*(mots/phrases) + 11.8*(syllabes/mots) - 15.59 -- niveau
scolaire US approximatif requis pour comprendre le texte.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv  # noqa: E402

NOM_MODELE = "lisibilite_flesch_kincaid"


def compter_syllabes(mot: str) -> int:
    """Heuristique standard : groupes de voyelles consecutives = 1 syllabe, 'e' muet final
    souvent retire, minimum 1 syllabe par mot."""
    mot = mot.lower()
    voyelles = "aeiouy"
    groupes = 0
    precedent_est_voyelle = False
    for c in mot:
        est_voyelle = c in voyelles
        if est_voyelle and not precedent_est_voyelle:
            groupes += 1
        precedent_est_voyelle = est_voyelle
    if mot.endswith("e") and groupes > 1:
        groupes -= 1
    return max(1, groupes)


def scores_flesch_kincaid(texte: str) -> tuple:
    phrases = [p.strip() for p in re.split(r"[.!?]", texte) if p.strip()]
    mots = re.findall(r"[A-Za-z]+", texte)
    if not phrases or not mots:
        raise SerieVide("texte vide ou non exploitable")

    n_mots = len(mots)
    n_phrases = len(phrases)
    n_syllabes = sum(compter_syllabes(m) for m in mots)

    mots_par_phrase = n_mots / n_phrases
    syllabes_par_mot = n_syllabes / n_mots

    reading_ease = 206.835 - 1.015 * mots_par_phrase - 84.6 * syllabes_par_mot
    grade_level = 0.39 * mots_par_phrase + 11.8 * syllabes_par_mot - 15.59
    return reading_ease, grade_level, n_mots, n_syllabes


def main() -> int:
    resultats = []

    votes_csv = BRUT / "fomc" / "votes.csv"
    if votes_csv.exists():
        import csv
        with votes_csv.open(encoding="utf-8") as f:
            lignes = sorted(csv.DictReader(f), key=lambda r: r["date"])
        if lignes:
            chemin_communique = BRUT / "fomc" / f"{lignes[-1]['date']}.txt"
            if chemin_communique.exists():
                try:
                    ease, grade, n_mots, n_syl = scores_flesch_kincaid(
                        chemin_communique.read_text(encoding="utf-8"))
                    resultats.append(("communique", lignes[-1]["date"], ease, grade, n_mots))
                except SerieVide as e:
                    print(f"communique : echec -- {e}")

    minutes_dir = BRUT / "fomc_minutes"
    fichiers_minutes = sorted(minutes_dir.glob("*.txt")) if minutes_dir.exists() else []
    if fichiers_minutes:
        dernier = fichiers_minutes[-1]
        try:
            ease, grade, n_mots, n_syl = scores_flesch_kincaid(
                dernier.read_text(encoding="utf-8"))
            resultats.append(("minutes", dernier.stem, ease, grade, n_mots))
        except SerieVide as e:
            print(f"minutes : echec -- {e}")

    if not resultats:
        print("echec -- ni communique ni minutes exploitables")
        return 1

    for type_doc, date_doc, ease, grade, n_mots in resultats:
        accumuler_csv(
            ETAT / f"{NOM_MODELE}.csv",
            ["type_document", "date", "reading_ease", "grade_level", "n_mots"],
            [[type_doc, date_doc, round(ease, 1), round(grade, 1), n_mots]],
        )
        print(f"OK -- {type_doc} ({date_doc}) : Reading Ease={ease:.1f} "
              f"(0=tres difficile, 100=tres facile), Grade Level={grade:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
