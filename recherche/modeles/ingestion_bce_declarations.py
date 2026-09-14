"""Ingestion -- declarations de politique monetaire de la BCE (ecb.europa.eu, source
officielle, aucune cle requise).

Comble le fait que la famille `nlp/` etait **100 % Fed** : 12 modeles tous braques sur le
FOMC, aucune autre banque centrale. Or une vue de change est relative par construction --
lire la Fed sans lire la BCE ne peut produire qu'une vue de taux americains.

Meme dispositif que `ingestion_fomc_statements.py`, adapte a la structure de la BCE.

**Separation communique / questions-reponses -- decision structurante, pas un detail.**
La page de la BCE s'intitule "Monetary policy statement (with Q&A)" et contient les deux :
la declaration preparee lue par la presidente, puis la seance de questions des journalistes.
Ce sont **deux registres linguistiques differents** -- un texte ecrit, relu et negocie d'un
cote, des reponses orales spontanees de l'autre. Les melanger fausserait toute mesure de ton,
de prudence ou de complexite comparee dans le temps (la part de Q&A varie d'une conference a
l'autre). Seule la **declaration preparee** est extraite ici : c'est elle qui correspond au
communique du FOMC et qui rend la comparaison Fed/BCE legitime.

Marqueurs verifies en direct sur deux conferences consecutives le 2026-09-14 (2026-07-23 et
2026-09-10), positions coherentes entre les deux :
- debut : "Good afternoon" (la declaration ouvre invariablement par
  "Good afternoon, the Vice-President and I welcome you to our press conference.")
- fin : "We are now ready" (phrase de bascule vers les questions :
  "We are now ready to take your questions.")

Le reste de la page (~16 000 caracteres de navigation et de scripts avant la declaration,
~20 000 de pied de page apres) est ecarte par ces bornes.

Usage :
    python ingestion_bce_declarations.py
"""

import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = "https://www.ecb.europa.eu"
INDEX_URL = (BASE + "/press/press_conference/monetary-policy-statement/{annee}/html/"
                    "index_include.en.html")
OUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "bce"
N_DECLARATIONS = 2

DEBUT_MARQUEUR = "Good afternoon"
FIN_MARQUEUR = "We are now ready"
MIN_CARACTERES = 1500  # une declaration preparee fait ~10 000 caracteres ; en dessous de
                        # 1500 c'est que les bornes ont attrape autre chose que le texte.

MOTIF_LIEN = re.compile(
    r"(/press/press_conference/monetary-policy-statement/\d{4}/html/"
    r"ecb\.is(\d{6})~[0-9a-f]+\.en\.html)")


def get_utf8(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    resp.encoding = "utf-8"  # meme precaution que pour le FOMC : ne pas laisser requests
                              # deviner l'encodage, les guillemets typographiques de la BCE
                              # deviennent illisibles sinon.
    return resp.text


def lister_declarations(n: int) -> list:
    """Retourne [(date ISO, url absolue)] des n declarations les plus recentes.

    L'annee courante peut etre vide en debut d'annee (aucune reunion encore tenue) : on
    remonte a l'annee precedente pour completer, plutot que de renvoyer une liste partielle.
    """
    annee = datetime.now(timezone.utc).year
    trouvees = {}
    for decalage in (0, 1):
        try:
            html = get_utf8(INDEX_URL.format(annee=annee - decalage))
        except requests.RequestException:
            continue
        for chemin, aaammjj in MOTIF_LIEN.findall(html):
            jour = datetime.strptime(aaammjj, "%y%m%d").date().isoformat()
            trouvees[jour] = BASE + chemin
        if len(trouvees) >= n:
            break
    if not trouvees:
        raise ValueError("aucune declaration trouvee sur les pages d'index de la BCE")
    return sorted(trouvees.items())[-n:]


def extraire_declaration(html: str) -> str:
    texte = re.sub(r"<[^>]+>", " ", html)
    texte = re.sub(r"\s+", " ", texte)
    debut = texte.find(DEBUT_MARQUEUR)
    fin = texte.find(FIN_MARQUEUR)
    if debut == -1 or fin == -1 or fin <= debut:
        raise ValueError("marqueurs de debut/fin introuvables -- structure de page inattendue")
    declaration = texte[debut:fin].strip()
    if len(declaration) < MIN_CARACTERES:
        raise ValueError(f"declaration de {len(declaration)} caracteres seulement -- "
                         f"les bornes n'ont pas attrape le bon bloc")
    return declaration


def main() -> int:
    try:
        declarations = lister_declarations(N_DECLARATIONS)
    except (ValueError, requests.RequestException) as e:
        print(f"echec de l'index BCE -- {e}")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lignes_index, echecs = [], []
    for jour, url in declarations:
        try:
            texte = extraire_declaration(get_utf8(url))
        except (ValueError, requests.RequestException) as e:
            echecs.append((jour, str(e)))
            print(f"{jour} : echec -- {e}")
            continue
        chemin = OUT_DIR / f"declaration_{jour}.txt"
        chemin.write_text(texte, encoding="utf-8")
        lignes_index.append((jour, len(texte), url))
        print(f"{jour} : {len(texte)} caracteres -> {chemin}")

    if lignes_index:
        index_csv = OUT_DIR / "declarations_index.csv"
        with index_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "n_caracteres", "url"])
            writer.writerows(lignes_index)
        print(f"index -> {index_csv}")

    if echecs:
        print(f"\n{len(echecs)}/{len(declarations)} declarations en echec")
        return 1
    print(f"\nOK -- {len(lignes_index)} declarations BCE ingerees")
    return 0


if __name__ == "__main__":
    sys.exit(main())
