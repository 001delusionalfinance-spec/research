"""Controle de coherence -- recoupe le taux Fed lu dans le communique FOMC (source primaire,
meme jour) contre le taux directeur publie par le BIS (`WS_CBPOL`, source de reference pour
le reste du depot, mais avec un delai de publication reel).

**Le probleme reel qu'il resout, trouve le 2026-09-17 en ecrivant une these dessus.** La Fed a
releve son taux de 25pb le 16/09/2026 (25260916, communique deja ingere le jour meme par
`ingestion_fomc_statements.py`). `divergence_taux_directeurs.csv` (source BIS) affichait encore
3,625% le lendemain -- le BIS n'avait tout simplement pas encore publie le nouveau chiffre
(verifie en direct sur `stats.bis.org` : `reportingEnd` du flux s'arretait au 15/09). Une these
entiere a ete ecrite sur la base du chiffre BIS perime, sans que rien dans le depot ne signale
l'ecart -- alors que le texte du communique, source plus fraiche, etait deja present dans
`donnees/brut/fomc/`. Ce controle ferme ce trou : il ne rafraichit rien de plus vite (le BIS
publie a son rythme, hors de portee de ce depot), il rend l'ecart VISIBLE au lieu de silencieux.

Bug annexe corrige le meme jour dans `ingestion_fomc_statements.py` : `extraire_taux()` ne
captait que la formule de statu quo ("federal funds rate AT X to Y percent"), jamais celle
d'un mouvement reel ("...TO X to Y percent") -- `taux_cible` restait vide silencieusement
exactement les fois ou la Fed bouge. Corrige avant que ce controle-ci ne soit ecrit, sinon il
n'aurait rien eu a comparer.

Usage :
    python controle_coherence_fed.py
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import BRUT  # noqa: E402

VOTES = BRUT / "fomc" / "votes.csv"
BIS_US = BRUT / "bis" / "taux_directeurs" / "US.csv"
SEUIL_ALERTE_PT = 0.05  # au dela, ce n'est plus un arrondi de representation -- un vrai ecart


def milieu_fourchette(texte: str) -> float:
    """"3-3/4 to 4" -> (3.75, 4.0) -> 3.875. "4 to 4-1/4" -> 4.125. Leve si format inattendu."""
    def valeur(morceau: str) -> float:
        morceau = morceau.strip()
        if "-" in morceau:
            entier, frac = morceau.split("-", 1)
            num, den = frac.split("/")
            return float(entier) + float(num) / float(den)
        return float(morceau)

    bas, haut = texte.split(" to ")
    return (valeur(bas) + valeur(haut)) / 2


def main() -> int:
    if not VOTES.exists():
        print(f"echec -- {VOTES} n'existe pas (ingestion_fomc_statements.py pas encore lance)")
        return 1
    if not BIS_US.exists():
        print(f"echec -- {BIS_US} n'existe pas")
        return 1

    with VOTES.open(encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    lignes_avec_taux = [l for l in lignes if l.get("taux_cible", "").strip()]
    if not lignes_avec_taux:
        print("OK -- aucun communique avec taux exploitable dans l'historique recent "
              "(silencieux, pas une erreur : peut arriver si les 2 derniers communiques "
              "sont anterieurs a la correction du 2026-09-17)")
        return 0

    derniere = lignes_avec_taux[-1]
    try:
        taux_fomc = milieu_fourchette(derniere["taux_cible"])
    except (ValueError, IndexError) as e:
        print(f"echec -- format de taux_cible inattendu ({derniere['taux_cible']!r}) : {e}")
        return 1

    with BIS_US.open(encoding="utf-8") as f:
        lignes_bis = [r for r in csv.DictReader(f) if r.get("taux", "").strip()]
    if not lignes_bis:
        print(f"echec -- {BIS_US} ne contient aucune valeur exploitable")
        return 1
    derniere_bis = lignes_bis[-1]
    taux_bis = float(derniere_bis["taux"])

    ecart = taux_fomc - taux_bis
    print(f"Communique FOMC du {derniere['date']} : {derniere['taux_cible']} "
          f"(milieu {taux_fomc:.3f}%)")
    print(f"BIS (WS_CBPOL, US), derniere observation {derniere_bis['date']} : {taux_bis:.3f}%")

    if abs(ecart) > SEUIL_ALERTE_PT:
        print(f"\nECART DETECTE : {ecart:+.3f}pt -- le BIS n'a probablement pas encore publie "
              f"la derniere decision Fed. Tout modele qui lit le taux directeur US depuis le "
              f"BIS (divergence_taux_directeurs.csv notamment) travaille sur un chiffre perime "
              f"jusqu'a ce que cet ecart se resorbe. Ne pas ecrire de these sur le taux Fed "
              f"sans avoir verifie ce controle en premier.")
        return 1

    print("\nOK -- coherent, le BIS reflete la derniere decision FOMC connue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
