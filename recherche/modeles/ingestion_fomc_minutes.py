"""Ingestion -- texte des 2 dernieres minutes FOMC (federalreserve.gov, source officielle,
aucune cle requise).

Distinct du communique (ingestion_fomc_statements.py, ~150 mots, publie le jour meme) : les
minutes sont publiees ~3 semaines apres, beaucoup plus riches (~5000-8000 mots de discussion
substantielle une fois le menu de navigation retire), incluent la lecture des marches par le
desk, le tour de table des participants, la discussion de politique.

Verifie en direct le 2026-09-08 : page listee sous `/monetarypolicy/fomcminutes<YYYYMMDD>.htm`
(motif different du communique, qui est sous `/newsevents/pressreleases/`). Corps substantiel
delimite par deux marqueurs stables verifies sur 2 minutes consecutives (2026-06-17,
2026-07-29) : "Developments in Financial Markets" (debut, section revue de marche du desk) et
"It was agreed that the next meeting" (fin, formule de cloture standard avant les mentions
administratives).

Usage :
    python ingestion_fomc_minutes.py
"""

import re
import sys
from pathlib import Path

import requests

CALENDAR_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
MINUTES_URL = "https://www.federalreserve.gov/monetarypolicy/fomcminutes{date}.htm"
OUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "fomc_minutes"
N_MINUTES = 2

DEBUT_MARQUEUR = "Developments in Financial Markets"
FIN_MARQUEUR = "It was agreed that the next meeting"


def get_utf8(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    resp.raise_for_status()
    resp.encoding = "utf-8"  # meme precaution que ingestion_fomc_statements.py -- bug deja
                              # trouve sur ce meme domaine
    return resp.text


def lister_dates_recentes(n: int) -> list:
    html = get_utf8(CALENDAR_URL)
    dates = sorted(set(re.findall(r"fomcminutes(\d{8})\.htm", html)))
    if not dates:
        raise ValueError("aucune date de minutes trouvee sur la page calendrier")
    return dates[-n:]


def extraire_texte(html: str) -> str:
    texte = re.sub(r"<[^>]+>", " ", html)
    texte = re.sub(r"\s+", " ", texte)
    debut = texte.find(DEBUT_MARQUEUR)
    fin = texte.find(FIN_MARQUEUR)
    if debut == -1 or fin == -1 or fin <= debut:
        raise ValueError("marqueurs de debut/fin introuvables -- structure de page inattendue")
    return texte[debut:fin].strip()


def main() -> int:
    try:
        dates = lister_dates_recentes(N_MINUTES)
    except (requests.RequestException, ValueError) as e:
        print(f"echec -- {e}")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    n_ok = 0
    echecs = []
    for d in dates:
        try:
            html = get_utf8(MINUTES_URL.format(date=d))
            texte = extraire_texte(html)
        except (requests.RequestException, ValueError) as e:
            echecs.append((d, str(e)))
            print(f"{d} : echec -- {e}")
            continue
        (OUT_DIR / f"{d}.txt").write_text(texte, encoding="utf-8")
        n_mots = len(texte.split())
        print(f"{d} : {n_mots} mots -> {OUT_DIR / f'{d}.txt'}")
        n_ok += 1

    if echecs:
        print(f"\n{len(echecs)}/{len(dates)} minutes en echec")
        return 1

    print(f"\nOK -- {n_ok} minutes ingerees")
    return 0


if __name__ == "__main__":
    sys.exit(main())
