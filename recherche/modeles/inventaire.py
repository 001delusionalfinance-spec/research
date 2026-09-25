"""Inventaire du dispositif -- compte ce qui existe reellement, plutot que ce qu'on croit.

Ecrit `rapports/inventaire.md` : nombre de series ingerees par source, de modeles enregistres,
de sorties produites.

**Pourquoi ce fichier existe.** MAP.md portait ces chiffres a la main. Ils ont derive le jour
meme de leur ecriture -- un audit du 2026-09-14 y a trouve "67 series" quand il y en avait 73,
"9 contrats" quand il y en avait 32, et "96 modeles" coexistant avec "111 modeles" dans le meme
fichier. Ce n'est pas un defaut d'attention : un chiffre recopie a la main dans un document
derive des que le code bouge, et il bouge tous les jours.

La regle qui en decoule, et qui vaut au-dela de ce fichier : **un chiffre qui decrit le depot
se compte, il ne s'ecrit pas.** MAP.md decrit desormais ce que fait le dispositif et pointe
ici pour les quantites.

Usage :
    python inventaire.py
"""

import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import BRUT, ETAT, REPO_ROOT, VISUALISATIONS  # noqa: E402

SORTIE = REPO_ROOT / "rapports" / "inventaire.md"
MODELES_DIR = Path(__file__).resolve().parent


def _compter_series_fred() -> int:
    source = (MODELES_DIR / "ingestion_fred.py").read_text(encoding="utf-8")
    bloc = re.search(r"SERIES = \[(.*?)\n\]", source, re.S)
    return len(re.findall(r'^\s*"([A-Z0-9]+)",', bloc.group(1), re.M)) if bloc else 0


def _compter_modeles() -> tuple:
    source = (MODELES_DIR / "run_all_modeles.py").read_text(encoding="utf-8")
    bloc = re.search(r"MODELES = \[(.*?)\n\]", source, re.S)
    entrees = re.findall(r'\("([^"]+)",\s*"([^"]+)"\)', bloc.group(1)) if bloc else []
    familles = {}
    for lane, _ in entrees:
        familles[lane] = familles.get(lane, 0) + 1
    return len(entrees), familles


def main() -> int:
    n_modeles, par_famille = _compter_modeles()

    sources = [
        ("FRED (series officielles)", _compter_series_fred()),
        ("BIS -- prix a la consommation", len(list((BRUT / "bis" / "cpi").glob("*.csv")))),
        ("BIS -- taux directeurs quotidiens",
         len(list((BRUT / "bis" / "taux_directeurs").glob("*.csv")))),
        ("BIS -- service de la dette",
         len(list((BRUT / "bis" / "service_dette").glob("*.csv")))),
        ("Courbes souveraines quotidiennes", len(list((BRUT / "souverains").glob("*.csv")))),
        ("Marches (FX, matieres, vol, indices)",
         len(list((BRUT / "marches").rglob("*.csv")))),
        ("Eurostat", len(list((BRUT / "eurostat").rglob("*.csv")))),
        ("Bilans de banques centrales", len(list((BRUT / "bilans").glob("*.csv")))),
        ("Positionnement CFTC", len(list((BRUT / "cftc").glob("*.csv")))),
        ("Tresor US", len(list((BRUT / "tresor_us").glob("*.csv")))),
        ("Indices et secteurs (yfinance)", len(list((BRUT / "yfinance").glob("*.csv")))),
    ]
    total_donnees = len(list(BRUT.rglob("*.csv")))
    n_etat = len(list(ETAT.glob("*.csv")))
    n_graphiques = len(list(VISUALISATIONS.rglob("*.png")))

    # Fraicheur, si le controle a deja tourne.
    fraicheur = ETAT / "fraicheur.csv"
    resume_fraicheur = "non calculee"
    if fraicheur.exists():
        verdicts = {}
        with fraicheur.open(encoding="utf-8") as f:
            for ligne in csv.DictReader(f):
                verdicts[ligne["verdict"]] = verdicts.get(ligne["verdict"], 0) + 1
        resume_fraicheur = ", ".join(f"{n} {v.lower()}" for v, n in sorted(verdicts.items()))

    lignes = [
        f"# Inventaire du dispositif -- "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", "",
        "Genere par `inventaire.py`. **Ne pas recopier ces chiffres ailleurs** : ils changent a "
        "chaque ajout, et une copie manuelle derive le jour meme (constate le 2026-09-14).", "",
        "## Donnees ingerees", "",
        "| Source | Fichiers |", "|---|---|",
    ]
    lignes += [f"| {nom} | {n} |" for nom, n in sources]
    lignes += [f"| **Total** | **{total_donnees}** |", "",
               f"Fraicheur : {resume_fraicheur}.", "",
               "## Modeles", "", "| Famille | Modeles |", "|---|---|"]
    lignes += [f"| {fam} | {n} |" for fam, n in sorted(par_famille.items())]
    lignes += [f"| **Total** | **{n_modeles}** |", "",
               "## Sorties", "",
               f"- {n_etat} fichiers de donnees (`rapports/donnees/`)",
               f"- {n_graphiques} graphiques utiles (`rapports/graphiques/`)",
               "- `rapports/lecture-du-jour.md`, `rapports/etat-recherche.xlsx`", ""]

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text("\n".join(lignes), encoding="utf-8")

    print(f"OK -- inventaire ecrit : {total_donnees} fichiers de donnees, {n_modeles} modeles "
          f"sur {len(par_famille)} familles, {n_etat} sorties, {n_graphiques} graphiques -> "
          f"{SORTIE.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
