"""Logique partagee par les modeles de recherche/modeles/ -- lue une fois, pas reimplementee
dans chaque modele. Porte depuis global-macro-desk-cloud (2026-09-08) : uniquement la partie
generique (lecture de serie, statistiques, graphiques) -- rien de specifique au fonds souverain
(pas de blotter/positions, aucune notion de book, ce depot n'en a pas)."""

import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BRUT = REPO_ROOT / "donnees" / "brut"
ETAT = REPO_ROOT / "rapports" / "donnees"
VISUALISATIONS = REPO_ROOT / "rapports" / "graphiques"


class SerieVide(Exception):
    """Leve quand une entree attendue manque ou est vide -- jamais un resultat silencieux."""


def read_series(path: Path, value_col: str = "value") -> list:
    """Lit un CSV date,<value_col> -- ignore les valeurs manquantes FRED notees '.'.
    Retourne une liste de (date_str, float) triee par date croissante."""
    import csv
    if not path.exists():
        raise SerieVide(f"{path} n'existe pas")
    out = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            v = row.get(value_col, "").strip()
            if v in ("", "."):
                continue
            out.append((row["date"], float(v)))
    if not out:
        raise SerieVide(f"{path} ne contient aucune valeur exploitable")
    out.sort(key=lambda t: t[0])
    return out


def latest(serie: list):
    return serie[-1][1]


def valeurs(serie: list) -> list:
    return [v for _, v in serie]


def percentile_rang(valeur: float, fenetre: list) -> float:
    """Rang en percentile de `valeur` au sein de `fenetre` (0-100)."""
    if not fenetre:
        raise SerieVide("fenetre vide pour le calcul de percentile")
    n_inferieur = sum(1 for v in fenetre if v <= valeur)
    return 100.0 * n_inferieur / len(fenetre)


def rendements_log(valeurs_prix: list) -> list:
    return [math.log(b / a) for a, b in zip(valeurs_prix, valeurs_prix[1:]) if a > 0 and b > 0]


def vol_annualisee(valeurs_prix: list, jours_par_an: int = 252) -> float:
    rendements = rendements_log(valeurs_prix)
    if len(rendements) < 2:
        raise SerieVide("pas assez de points pour calculer une vol realisee")
    moyenne = sum(rendements) / len(rendements)
    variance = sum((r - moyenne) ** 2 for r in rendements) / (len(rendements) - 1)
    return math.sqrt(variance) * math.sqrt(jours_par_an)


def correlation(a: list, b: list) -> float:
    n = min(len(a), len(b))
    if n < 3:
        raise SerieVide("pas assez de points communs pour une correlation")
    a, b = a[-n:], b[-n:]
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va == 0 or vb == 0:
        raise SerieVide("variance nulle -- correlation non definie")
    return cov / math.sqrt(va * vb)


def correlation_avec_p_valeur(a: list, b: list) -> tuple:
    """Correlation de Pearson + p-valeur (test t bilateral, H0 : rho=0). A utiliser des qu'on
    scanne plusieurs paires a la fois -- une correlation sans test de significativite peut
    induire en erreur."""
    from scipy import stats
    r = correlation(a, b)
    n = min(len(a), len(b))
    if n <= 2:
        raise SerieVide("pas assez de points pour un test de significativite (n<=2)")
    if abs(r) >= 1.0:
        return r, 0.0
    t = r * ((n - 2) ** 0.5) / ((1 - r ** 2) ** 0.5)
    p = float(2 * (1 - stats.t.cdf(abs(t), df=n - 2)))
    return r, p


def seuils_bonferroni(p_valeurs: list, alpha: float = 0.05) -> list:
    """Significatif apres correction pour tests multiples simultanes (Bonferroni). Retourne une
    liste de booleens dans le meme ordre que `p_valeurs`."""
    n = len(p_valeurs)
    if n == 0:
        return []
    seuil = alpha / n
    return [p < seuil for p in p_valeurs]


def ecrire_csv(path: Path, header: list, lignes: list) -> None:
    """Ecrase -- pour un etat courant (pas un historique)."""
    import csv
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(lignes)


def _indices_cle_naturelle(header: list, lignes: list) -> list:
    """Deduit la cle d'un historique date sans connaitre le modele.

    La date est toujours incluse. Les colonnes placees avant elle sont des identifiants
    (institution, bloc, contrat...). Si plusieurs lignes du meme lot ont encore la meme cle,
    on ajoute les colonnes suivantes jusqu'a obtenir une cle unique. Exemples :

    - ``date`` pour une observation unique par jour ;
    - ``date, horizon`` pour le chemin de taux Fed ;
    - ``bloc, date`` pour une observation par bloc et par jour.

    Un fichier sans colonne temporelle conserve l'ancien comportement de deduplication par
    ligne complete : aucune cle metier ne peut alors etre inventee sans ambiguite.
    """
    noms = [str(c).strip().lower() for c in header]
    indices_date = [i for i, nom in enumerate(noms)
                    if nom == "date" or nom.startswith("date_") or nom.endswith("_date")]
    if not indices_date:
        return list(range(len(header)))

    index_date = indices_date[0]
    indices = list(range(index_date + 1))
    # Certains modeles ecrivent une dimension a la fois (positionnement COT, par exemple).
    # On ne peut donc pas se fier uniquement aux doublons du lot entrant pour decouvrir la
    # dimension. Ces noms ont un sens d'identifiant stable dans les schemas du depot.
    dimensions_connues = {
        "horizon", "bloc", "contrat", "marche", "feature", "scenario", "secteur",
        "serie", "type_document", "institution", "ticker",
    }
    for i, nom in enumerate(noms):
        if i > index_date and nom in dimensions_connues and i not in indices:
            indices.append(i)
    lignes_texte = [[str(v) for v in ligne] for ligne in lignes]
    while len(indices) < len(header):
        cles = [tuple(ligne[i] if i < len(ligne) else "" for i in indices)
                for ligne in lignes_texte]
        if len(cles) == len(set(cles)):
            break
        prochain = next(i for i in range(len(header)) if i not in indices)
        indices.append(prochain)
        indices.sort()
    return indices


def accumuler_csv(path: Path, header: list, lignes: list, key_columns: list | None = None) -> None:
    """Insere ou remplace des observations dans un historique CSV.

    L'ancienne implementation ne dedupliquait que des lignes strictement identiques. Une
    correction portant sur une observation deja publiee creait donc deux verites pour la meme
    date -- c'est exactement ce qui s'est produit pour ``ton_fomc`` le 2026-09-16.

    La cle est deduite de la colonne temporelle et des dimensions necessaires pour rendre le
    lot entrant unique. Elle peut etre imposee avec ``key_columns`` pour les schemas atypiques.
    Les doublons deja presents sont nettoyes en conservant leur derniere version.

    Un changement d'en-tete reconstruit toujours le fichier : des lignes issues de deux schemas
    differents ne sont pas comparables.
    """
    import csv

    if not lignes:
        return
    header_texte = [str(c) for c in header]
    lignes_texte = [[str(v) for v in ligne] for ligne in lignes]
    if any(len(ligne) != len(header_texte) for ligne in lignes_texte):
        raise ValueError(f"{path.name}: une ligne n'a pas {len(header_texte)} colonnes")

    path.parent.mkdir(parents=True, exist_ok=True)
    existantes = []
    entete_actuelle = None
    if path.exists():
        with path.open(encoding="utf-8", newline="") as f:
            lecteur = csv.reader(f)
            entete_actuelle = next(lecteur, None)
            existantes = [row for row in lecteur if row]

    if entete_actuelle is not None and entete_actuelle != header_texte:
        print(f"  [{path.name}] en-tete modifie "
              f"({len(entete_actuelle)} -> {len(header_texte)} colonnes) : fichier reconstruit, "
              f"l'historique ecrit sous l'ancien schema n'etait plus comparable")
        existantes = []

    if key_columns is None:
        indices_cle = _indices_cle_naturelle(header_texte, lignes_texte)
    else:
        inconnues = [nom for nom in key_columns if nom not in header_texte]
        if inconnues:
            raise ValueError(f"{path.name}: colonnes de cle inconnues: {inconnues}")
        indices_cle = [header_texte.index(nom) for nom in key_columns]

    def cle(ligne: list) -> tuple:
        return tuple(ligne[i] if i < len(ligne) else "" for i in indices_cle)

    # Un dictionnaire ordonne preserve la position historique de la premiere occurrence, mais
    # la valeur de la derniere occurrence gagne : une correction remplace l'ancienne version.
    par_cle = {}
    for ligne in existantes + lignes_texte:
        if len(ligne) == len(header_texte):
            par_cle[cle(ligne)] = ligne
    resultat = list(par_cle.values())

    if entete_actuelle == header_texte and resultat == existantes:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header_texte)
        w.writerows(resultat)


def lire_historique(path: Path) -> list:
    import csv
    if not path.exists():
        raise SerieVide(f"{path} n'existe pas")
    with path.open(encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    if not lignes:
        raise SerieVide(f"{path} est vide")
    return lignes


# --- Graphiques : style commun, sobre, noir sur blanc. ---

def _configurer_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "black",
        "axes.labelcolor": "black",
        "text.color": "black",
        "xtick.color": "black",
        "ytick.color": "black",
        "axes.grid": True,
        "grid.color": "#dddddd",
        "grid.linewidth": 0.6,
        "font.size": 10,
    })
    return plt


def nouvelle_figure(figsize=(8, 5), nrows=1, ncols=1):
    plt = _configurer_matplotlib()
    fig, ax = plt.subplots(nrows, ncols, figsize=figsize)
    return plt, fig, ax


def sauvegarder_figure(plt, fig, modele: str, nom: str) -> Path:
    """Ecrit rapports/graphiques/<modele>/<nom>.png -- un sous-dossier par modele."""
    dossier = VISUALISATIONS / modele
    dossier.mkdir(parents=True, exist_ok=True)
    out_path = dossier / f"{nom}.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
