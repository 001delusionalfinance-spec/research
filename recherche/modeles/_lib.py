"""Logique partagee par les modeles de recherche/modeles/ -- lue une fois, pas reimplementee
dans chaque modele. Porte depuis global-macro-desk-cloud (2026-09-08) : uniquement la partie
generique (lecture de serie, statistiques, graphiques) -- rien de specifique au fonds souverain
(pas de blotter/positions, aucune notion de book, ce depot n'en a pas)."""

import math
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BRUT = REPO_ROOT / "donnees" / "brut"
ETAT = REPO_ROOT / "recherche" / "etat"
VISUALISATIONS = REPO_ROOT / "recherche" / "visualisations"


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


def accumuler_csv(path: Path, header: list, lignes: list) -> None:
    """Ajoute des lignes a l'historique -- n'ecrase jamais. Deduplique les lignes strictement
    identiques a une ligne deja presente."""
    import csv
    path.parent.mkdir(parents=True, exist_ok=True)
    nouveau = not path.exists()
    existantes = set()
    if not nouveau:
        with path.open(encoding="utf-8") as f:
            for row in csv.reader(f):
                existantes.add(tuple(row))
    lignes_a_ecrire = [l for l in lignes if tuple(str(v) for v in l) not in existantes]
    if not lignes_a_ecrire:
        return
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nouveau:
            w.writerow(header)
        w.writerows(lignes_a_ecrire)


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
    """Ecrit recherche/visualisations/<modele>/<nom>.png -- un sous-dossier par modele."""
    dossier = VISUALISATIONS / modele
    dossier.mkdir(parents=True, exist_ok=True)
    out_path = dossier / f"{nom}.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
