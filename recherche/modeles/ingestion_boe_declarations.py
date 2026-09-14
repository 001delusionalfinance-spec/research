"""Ingestion -- resumes de politique monetaire de la Banque d'Angleterre.

Troisieme banque centrale ajoutee a la famille `nlp/`, apres la Fed et la BCE. Choix assume :
la couverture NLP ne vise PAS les douze blocs a poids egal. Un desk macro lit la Fed et la BCE
de pres, puis la BOJ et la Banque d'Angleterre ; le Riksbank ou la Norges Bank ne pesent
presque rien dans une lecture de marche. Compter "2 banques sur 12" surestimait donc le trou --
ce qui manquait vraiment, c'etait la BoE et la BOJ.

**La BOJ n'est pas ici, et pour une raison precise** : ses declarations de politique monetaire
sont publiees en **PDF** (`k260731a.pdf` et similaires), pas en HTML. Les extraire demanderait
d'ajouter une dependance de lecture PDF a une chaine d'integration partagee par 96 modeles --
un risque sans rapport avec le besoin. A traiter separement si le sujet devient prioritaire.

Reperage des publications : le flux d'actualites de la BoE melange tous les sujets (billets,
infrastructures de paiement, discours). Les decisions de politique monetaire sont isolees par
motif sur le titre -- elles s'intitulent invariablement "Bank Rate maintained/increased/reduced
at X% - <Mois> <Annee> Monetary Policy Summary and Minutes".

Bornes d'extraction verifiees sur deux publications consecutives (juillet et juin 2026) :
- debut : le titre de section date ("Monetary Policy Summary, July 2026"). Attention, la
  chaine "Monetary Policy Summary" apparait aussi des le caractere 42, dans le titre de la
  page -- viser cette premiere occurrence ramenerait tout le menu de navigation. D'ou la
  recherche par expression datee.
- fin : la PREMIERE borne rencontree parmi plusieurs candidates. Premiere version fautive
  corrigee au test : s'arreter a "Back to top" laissait passer un bloc de navigation en fin
  d'extraction ("... View more Other Monetary Policy Committee news"), c'est-a-dire des titres
  d'autres publications colles au texte. Sans consequence visible a la lecture, mais fatal pour
  une mesure de ton ou de complexite -- ces titres parasites varient d'une publication a
  l'autre et pollueraient la comparaison dans le temps.

Usage :
    python ingestion_boe_declarations.py
"""

import csv
import re
import sys
from datetime import datetime
from pathlib import Path

import requests

RSS_URL = "https://www.bankofengland.co.uk/rss/news"
OUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "boe"
N_PUBLICATIONS = 2

MOTIF_TITRE_MPC = re.compile(r"monetary policy summary|bank rate (maintained|increased|reduced)",
                             re.I)
MOTIF_DEBUT = re.compile(r"Monetary Policy Summary,\s+\w+\s+2\d{3}")
# Bornes de fin candidates, la plus proche du debut gagne. "Back to top" reste en dernier
# recours : c'est la fin de page, donc la borne la plus large.
FINS_CANDIDATES = ("Other Monetary Policy Committee news", "Related links", "Back to top")
MIN_CARACTERES = 2000


def get_utf8(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    resp.encoding = "utf-8"  # meme precaution que pour la Fed et la BCE : ne pas laisser
                              # requests deviner l'encodage.
    return resp.text


def lister_publications(n: int) -> list:
    """Retourne [(date ISO, titre, url)] des n dernieres decisions de politique monetaire."""
    flux = get_utf8(RSS_URL)
    trouvees = []
    for bloc in re.findall(r"<item[ >].*?</item>", flux, re.S):
        titre_brut = re.search(r"<title[^>]*>(.*?)</title>", bloc, re.S)
        lien_brut = re.search(r"<link[^>]*>(.*?)</link>", bloc, re.S)
        date_brute = re.search(r"<pubDate[^>]*>(.*?)</pubDate>", bloc, re.S)
        if not (titre_brut and lien_brut):
            continue
        titre = re.sub(r"<!\[CDATA\[|\]\]>", "", titre_brut.group(1)).strip()
        if not MOTIF_TITRE_MPC.search(titre):
            continue
        lien = re.sub(r"<!\[CDATA\[|\]\]>", "", lien_brut.group(1)).strip()
        jour = ""
        if date_brute:
            try:
                jour = datetime.strptime(
                    date_brute.group(1).strip()[:16], "%a, %d %b %Y").date().isoformat()
            except ValueError:
                jour = ""
        trouvees.append((jour, titre, lien))
    if not trouvees:
        raise ValueError("aucune decision de politique monetaire trouvee dans le flux BoE")
    return sorted(trouvees)[-n:]


def extraire(html: str) -> str:
    texte = re.sub(r"<[^>]+>", " ", html)
    texte = re.sub(r"\s+", " ", texte)
    debut_trouve = MOTIF_DEBUT.search(texte)
    if not debut_trouve:
        raise ValueError("titre de section date introuvable -- structure de page inattendue")
    positions = [texte.find(marqueur, debut_trouve.start()) for marqueur in FINS_CANDIDATES]
    positions = [p for p in positions if p != -1]
    if not positions:
        raise ValueError(f"aucune borne de fin trouvee parmi {FINS_CANDIDATES}")
    contenu = texte[debut_trouve.start():min(positions)].strip()
    if len(contenu) < MIN_CARACTERES:
        raise ValueError(f"contenu de {len(contenu)} caracteres seulement -- bornes suspectes")
    return contenu


def main() -> int:
    try:
        publications = lister_publications(N_PUBLICATIONS)
    except (ValueError, requests.RequestException) as e:
        print(f"echec du flux BoE -- {e}")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index, echecs = [], []
    for jour, titre, url in publications:
        etiquette = jour or url.rsplit("/", 1)[-1]
        try:
            texte = extraire(get_utf8(url))
        except (ValueError, requests.RequestException) as e:
            echecs.append((etiquette, str(e)))
            print(f"{etiquette} : echec -- {e}")
            continue
        chemin = OUT_DIR / f"resume_{etiquette}.txt"
        chemin.write_text(texte, encoding="utf-8")
        index.append((jour, titre, len(texte), url))
        print(f"{etiquette} : {len(texte)} caracteres -> {chemin}")

    if index:
        chemin_index = OUT_DIR / "resumes_index.csv"
        with chemin_index.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "titre", "n_caracteres", "url"])
            writer.writerows(index)
        print(f"index -> {chemin_index}")

    if echecs:
        print(f"\n{len(echecs)}/{len(publications)} publications en echec")
        return 1
    print(f"\nOK -- {len(index)} resumes de politique monetaire BoE ingeres")
    return 0


if __name__ == "__main__":
    sys.exit(main())
