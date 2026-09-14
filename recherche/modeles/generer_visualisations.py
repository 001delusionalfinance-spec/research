"""Generation des apercus graphiques, un par fichier d'etat.

Produit `recherche/visualisations/<modele>/apercu.png` pour chaque sortie de modele.

**Pourquoi generique plutot qu'un graphique ecrit dans chaque modele.** Quatre modeles sur cent
onze produisaient une figure ; ajouter du code de trace dans les cent sept autres aurait
demande de les modifier un par un, avec un risque de regression sans rapport avec le besoin.
Les fichiers d'etat ont deja une structure reguliere -- une colonne de date ou une colonne
d'entites, puis des colonnes numeriques -- et cette regularite suffit a produire un apercu
correct sans toucher aux modeles.

Deux formes, choisies d'apres la structure du fichier et non d'apres son nom :
- **serie temporelle** quand la premiere colonne contient des dates -- courbe par colonne
  numerique ;
- **comparaison** quand la premiere colonne contient des entites (pays, devises, contrats) --
  barres horizontales triees sur la colonne numerique la plus informative.

Un apercu n'est pas une figure d'analyse. Il sert a voir d'un coup d'oeil si une sortie est
plausible et ou elle en est ; un modele qui merite une figure travaillee garde la sienne, ecrite
chez lui.
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ETAT, VISUALISATIONS, nouvelle_figure, sauvegarder_figure  # noqa: E402

MAX_SERIES_TRACEES = 6      # au-dela, la figure devient illisible
MAX_BARRES = 20
MIN_POINTS_SERIE = 3
FORMATS_DATE = ("%Y-%m-%d", "%Y-%m")


def _est_date(texte: str) -> bool:
    texte = texte.strip()
    if "-Q" in texte:
        return True
    return any(_essai_date(texte, f) for f in FORMATS_DATE)


def _essai_date(texte: str, motif: str) -> bool:
    try:
        datetime.strptime(texte, motif)
        return True
    except ValueError:
        return False


def _nombre(texte):
    try:
        return float(str(texte).strip())
    except (TypeError, ValueError):
        return None


def _lire(chemin: Path):
    with chemin.open(encoding="utf-8", newline="") as f:
        lignes = list(csv.reader(f))
    if len(lignes) < 2:
        return None, None
    return lignes[0], lignes[1:]


def _colonnes_numeriques(entete: list, donnees: list) -> list:
    """Indices des colonnes majoritairement numeriques, hors premiere colonne."""
    retenues = []
    for i in range(1, len(entete)):
        valeurs = [_nombre(l[i]) for l in donnees if i < len(l)]
        exploitables = [v for v in valeurs if v is not None]
        if valeurs and len(exploitables) / len(valeurs) >= 0.8:
            retenues.append(i)
    return retenues


def _tracer_serie(nom: str, entete: list, donnees: list, colonnes: list) -> Path:
    plt, fig, ax = nouvelle_figure(figsize=(10, 5))
    for i in colonnes[:MAX_SERIES_TRACEES]:
        points = [(l[0], _nombre(l[i])) for l in donnees if i < len(l)]
        points = [(d, v) for d, v in points if v is not None]
        if len(points) < MIN_POINTS_SERIE:
            continue
        ax.plot([d for d, _ in points], [v for _, v in points], label=entete[i], linewidth=1.2)
    ax.set_title(nom.replace("_", " "))
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    # Une serie longue rendrait l'axe illisible : on ne garde qu'une dizaine de reperes.
    etiquettes = ax.get_xticks()
    if len(etiquettes) > 12:
        ax.set_xticks(etiquettes[:: max(1, len(etiquettes) // 10)])
    if len(colonnes) > 1:
        ax.legend(fontsize=7)
    return sauvegarder_figure(plt, fig, nom, "apercu")


def _colonne_la_plus_discriminante(donnees: list, colonnes: list) -> int:
    """Colonne qui separe le mieux les entites, mesuree par son coefficient de variation.

    Prendre la premiere colonne numerique venue donnait des apercus a cote du sujet : sur les
    pentes de courbes, cela tracait le taux court alors que l'information du modele est la
    pente elle-meme. Le coefficient de variation (ecart-type rapporte a la moyenne des valeurs
    absolues) retient la colonne ou les entites different le plus les unes des autres, ce qui
    est par construction celle qui porte le contraste -- et ce critere se mesure sur les
    donnees, sans dependre du nom des colonnes.
    """
    meilleure, meilleur_score = colonnes[0], -1.0
    for i in colonnes:
        valeurs = [v for v in (_nombre(l[i]) for l in donnees if i < len(l)) if v is not None]
        if len(valeurs) < 2:
            continue
        moyenne_abs = sum(abs(v) for v in valeurs) / len(valeurs)
        if moyenne_abs == 0:
            continue
        centre = sum(valeurs) / len(valeurs)
        ecart = (sum((v - centre) ** 2 for v in valeurs) / (len(valeurs) - 1)) ** 0.5
        score = ecart / moyenne_abs
        if score > meilleur_score:
            meilleure, meilleur_score = i, score
    return meilleure


def _tracer_comparaison(nom: str, entete: list, donnees: list, colonnes: list) -> Path:
    colonne = _colonne_la_plus_discriminante(donnees, colonnes)
    paires = [(l[0], _nombre(l[colonne])) for l in donnees if colonne < len(l)]
    paires = [(e, v) for e, v in paires if v is not None][:MAX_BARRES]
    if not paires:
        raise ValueError("aucune valeur numerique a tracer")
    paires.sort(key=lambda t: t[1])
    plt, fig, ax = nouvelle_figure(figsize=(9, max(3, 0.35 * len(paires) + 1)))
    ax.barh([e for e, _ in paires], [v for _, v in paires],
            color=["#b02418" if v < 0 else "#1f5f8b" for _, v in paires])
    ax.set_title(f"{nom.replace('_', ' ')} -- {entete[colonne]}")
    ax.tick_params(axis="y", labelsize=8)
    ax.axvline(0, color="black", linewidth=0.8)
    # La grille par defaut du depot est active sur les deux axes ; sur un graphique en barres
    # horizontales, les lignes horizontales traversent le milieu de chaque barre et donnent
    # l'impression d'une barre coupee en deux. On ne garde que la grille verticale, qui elle
    # aide vraiment a lire la valeur.
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    return sauvegarder_figure(plt, fig, nom, "apercu")


def main() -> int:
    fichiers = sorted(ETAT.glob("*.csv"))
    if not fichiers:
        print(f"echec -- aucun fichier d'etat dans {ETAT}")
        return 1

    n_series, n_comparaisons, ignores = 0, 0, []
    for chemin in fichiers:
        nom = chemin.stem
        try:
            entete, donnees = _lire(chemin)
            if not entete:
                ignores.append((nom, "fichier vide ou sans donnees"))
                continue
            colonnes = _colonnes_numeriques(entete, donnees)
            if not colonnes:
                ignores.append((nom, "aucune colonne numerique"))
                continue
            if _est_date(donnees[0][0]) and len(donnees) >= MIN_POINTS_SERIE:
                _tracer_serie(nom, entete, donnees, colonnes)
                n_series += 1
            else:
                _tracer_comparaison(nom, entete, donnees, colonnes)
                n_comparaisons += 1
        except (OSError, ValueError, IndexError) as e:
            ignores.append((nom, str(e)))

    print(f"OK -- {n_series + n_comparaisons} apercus generes dans {VISUALISATIONS.name}/ "
          f"({n_series} series temporelles, {n_comparaisons} comparaisons)")
    if ignores:
        print(f"   {len(ignores)} sortie(s) sans apercu : {[n for n, _ in ignores][:8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
