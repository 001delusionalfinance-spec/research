"""Ingestion -- texte des 2 derniers communiques FOMC (federalreserve.gov, source officielle,
aucune cle requise).

Verifie en direct le 2026-09-08 : la page calendrier (`fomccalendars.htm`) liste les
communiques sous le motif `/newsevents/pressreleases/monetary<YYYYMMDD>a.htm`. Le texte utile
est noye dans ~8000 caracteres de menu de navigation avant de commencer -- delimite par deux
marqueurs stables verifies sur 2 communiques consecutifs (2026-06-17 et 2026-07-29) : "The
Committee decided" (debut) et "For media inquiries" (fin).

**Trois bugs reels trouves en testant sur les 2 vrais communiques (2026-06-17, 2026-07-29),
pas supposes** :
1. `requests` devinait mal l'encodage de la reponse (le site ne declare pas `charset=utf-8`
   explicitement dans son Content-Type) -- le tiret cadratin de "9 - 3 vote" devenait illisible
   (mojibake UTF-8 relu en Latin-1), cassant la regex de decompte des voix. Corrige en forcant
   `resp.encoding = "utf-8"` avant de lire `.text`.
2. Le decompte de voix ("approved the following statement for release by a 9 - 3 vote:")
   precede DEBUT_MARQUEUR dans la page -- hors de `texte_statement`. Chercher sur la page
   entiere sans borne a fait remonter la regex jusqu'au bas de page (aucun ":" proche pour
   ancrer la recherche), capturant tout le menu de navigation. Corrige en limitant la recherche
   a une fenetre de 80 caracteres autour de "approved the following statement".
3. L'extraction des dissidents cassait sur "Beth M. Hammack" (le point de l'initiale du milieu
   coupait un `[^.]+` premature). Corrige en capturant avec `.+?` jusqu'au marqueur ", who
   preferred" qui suit toujours la liste de noms, plutot que de s'arreter au premier point.

Usage :
    python ingestion_fomc_statements.py
"""

import csv
import re
import sys
from pathlib import Path

import requests

CALENDAR_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
STATEMENT_URL = "https://www.federalreserve.gov/newsevents/pressreleases/monetary{date}a.htm"
OUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "fomc"
N_STATEMENTS = 2

DEBUT_MARQUEUR = "The Committee decided"
FIN_MARQUEUR = "For media inquiries"


def get_utf8(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    resp.raise_for_status()
    resp.encoding = "utf-8"  # cf. bug 1 documente en tete de fichier -- ne jamais faire
                              # confiance a la detection automatique d'encodage de requests ici
    return resp.text


def lister_dates_recentes(n: int) -> list:
    html = get_utf8(CALENDAR_URL)
    dates = sorted(set(re.findall(r"monetary(\d{8})a\.htm", html)))
    if not dates:
        raise ValueError("aucune date de communique trouvee sur la page calendrier")
    return dates[-n:]


def extraire_texte(html: str) -> str:
    texte = re.sub(r"<[^>]+>", " ", html)
    texte = re.sub(r"\s+", " ", texte)
    debut = texte.find(DEBUT_MARQUEUR)
    fin = texte.find(FIN_MARQUEUR)
    if debut == -1 or fin == -1 or fin <= debut:
        raise ValueError("marqueurs de debut/fin introuvables -- structure de page inattendue")
    return texte[debut:fin].strip()


def extraire_vote(texte_page: str, texte_statement: str) -> tuple:
    """Retourne (pour, contre, dissidents) -- dissidents = [] si vote unanime.

    Le decompte ("by a 9 - 3 vote") precede le marqueur DEBUT_MARQUEUR dans la page (avant
    "The Committee decided"), donc cherche dans `texte_page`, mais avec une fenetre bornee a
    ~60 caracteres autour de "approved the following statement" -- jamais un `.search` ouvert
    sur la page entiere (cf. bug 2 en tete de fichier).
    Les dissidents, eux, sont dans `texte_statement` (deja borne). Noms comme "Beth M. Hammack"
    contiennent un point (initiale du milieu) -- capture avec `.+?` (pas `[^.]+?`) jusqu'au
    marqueur ", who preferred" qui suit toujours la liste de noms dans un communique FOMC."""
    i = texte_page.find("approved the following statement")
    pour, contre = None, None
    if i != -1:
        fenetre = texte_page[i:i + 80]
        m = re.search(r"by a (\d+)\s*[\-‐–—]\s*(\d+) vote", fenetre)
        if m:
            pour, contre = int(m.group(1)), int(m.group(2))

    m2 = re.search(r"Voting against[^:]*?were (.+?), who preferred", texte_statement)
    dissidents = [n.strip() for n in re.split(r",| and ", m2.group(1)) if n.strip()] if m2 else []
    return pour, contre, dissidents


def extraire_taux(texte_statement: str) -> str:
    m = re.search(r"federal funds rate at ([\d/\- to]+) percent", texte_statement)
    return m.group(1).strip() if m else ""


def main() -> int:
    try:
        dates = lister_dates_recentes(N_STATEMENTS)
    except (requests.RequestException, ValueError) as e:
        print(f"echec -- {e}")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    resultats = []
    echecs = []
    for d in dates:
        try:
            html = get_utf8(STATEMENT_URL.format(date=d))
            texte_page = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
            texte_statement = extraire_texte(html)
            pour, contre, dissidents = extraire_vote(texte_page, texte_statement)
            taux = extraire_taux(texte_statement)
        except (requests.RequestException, ValueError) as e:
            echecs.append((d, str(e)))
            print(f"{d} : echec -- {e}")
            continue

        (OUT_DIR / f"{d}.txt").write_text(texte_statement, encoding="utf-8")
        resultats.append([d, pour, contre, ";".join(dissidents), taux])
        print(f"{d} : vote {pour}-{contre}, {len(dissidents)} dissident(s), taux={taux}")

    if resultats:
        with (OUT_DIR / "votes.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["date", "pour", "contre", "dissidents", "taux_cible"])
            w.writerows(resultats)

    if echecs:
        print(f"\n{len(echecs)}/{len(dates)} communiques en echec")
        return 1

    print(f"\nOK -- {len(resultats)} communiques ingeres")
    return 0


if __name__ == "__main__":
    sys.exit(main())
