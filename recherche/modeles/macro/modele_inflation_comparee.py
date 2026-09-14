"""Modele -- inflation comparee entre les 12 blocs economiques suivis.

Lit les indices de prix du BIS (`donnees/brut/bis/cpi/`) et calcule le glissement annuel de
chacun. L'ingestion stocke l'INDICE brut, jamais un taux : transformer est le travail d'un
modele, pas de l'ingestion.

Ce que ca repond : qui desinflate, qui reaccelere, et surtout **quelle est la dispersion entre
blocs**. Une inflation a 3% partout n'appelle pas la meme lecture qu'une moyenne de 3% avec la
zone euro a 1% et les Etats-Unis a 5% -- le second cas force les banques centrales a diverger,
donc deplace les differentiels de taux, donc le change.

Limite assumee : indice tous postes, pas de sous-jacent (le BIS ne publie pas le core dans ce
jeu). Un choc energetique temporaire s'y lit comme de l'inflation, ce qu'une banque centrale
regarderait differemment.
"""

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, ecrire_csv, read_series  # noqa: E402

NOM_MODELE = "inflation_comparee"
CPI_DIR = BRUT / "bis" / "cpi"

BLOCS = {
    "US": "Etats-Unis", "XM": "Zone euro", "GB": "Royaume-Uni", "JP": "Japon",
    "CN": "Chine", "KR": "Coree", "CA": "Canada", "AU": "Australie",
    "CH": "Suisse", "SE": "Suede", "NO": "Norvege", "NZ": "Nouvelle-Zelande",
}


def glissement_annuel(serie: list) -> tuple:
    """(inflation en %, periode). Compare a la meme periode de l'annee precedente, en
    remontant dans la serie plutot qu'en supposant 12 pas -- les series trimestrielles
    (Australie, Nouvelle-Zelande) n'ont que 4 pas par an."""
    derniere_periode, derniere_valeur = serie[-1]
    annee, reste = derniere_periode.split("-")[0], derniere_periode.split("-")[1]
    cible = f"{int(annee) - 1}-{reste}"
    correspondances = [v for p, v in serie if p == cible]
    if not correspondances:
        raise SerieVide(f"pas d'observation a {cible} pour le glissement annuel")
    return (derniere_valeur / correspondances[0] - 1) * 100, derniere_periode


def main() -> int:
    lignes, echecs = [], []
    for code, nom in BLOCS.items():
        try:
            serie = read_series(CPI_DIR / f"{code}.csv", "indice")
            inflation, periode = glissement_annuel(serie)
            lignes.append((nom, code, periode, round(inflation, 2)))
        except (SerieVide, ValueError) as e:
            echecs.append((nom, str(e)))

    if not lignes:
        print(f"echec -- aucun bloc exploitable ({len(echecs)} en erreur)")
        return 1

    lignes.sort(key=lambda l: -l[3])
    valeurs = [l[3] for l in lignes]
    dispersion = max(valeurs) - min(valeurs)
    mediane = statistics.median(valeurs)

    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["bloc", "code", "periode", "inflation_annuelle_pct"], lignes)

    plus_haut, plus_bas = lignes[0], lignes[-1]
    if dispersion > 3.0:
        lecture = ("dispersion forte -- les banques centrales sont poussees a diverger, "
                   "ce qui deplace les differentiels de taux et le change")
    elif dispersion > 1.5:
        lecture = "dispersion moderee entre blocs"
    else:
        lecture = "blocs alignes -- peu de pression a la divergence monetaire"

    print(f"OK -- inflation annuelle sur {len(lignes)} blocs : mediane {mediane:.2f}%, "
          f"dispersion {dispersion:.2f}pt ({plus_haut[0]} {plus_haut[3]:+.2f}% au plus haut, "
          f"{plus_bas[0]} {plus_bas[3]:+.2f}% au plus bas) -- {lecture}")
    if echecs:
        print(f"   {len(echecs)} bloc(s) non exploitable(s) : {[n for n, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
