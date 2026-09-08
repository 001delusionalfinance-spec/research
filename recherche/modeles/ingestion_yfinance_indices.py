"""Ingestion yfinance -- indices de reference (S&P 500, VIX) + 10 ETF sectoriels, historique
30 ans pour SP500/VIX (etendu le 2026-09-08, initialement 2 ans).

Etendu a 30 ans pour modele_var_drawdown.py / stress-testing (famille risque) -- besoin de
couvrir 2008 et 2020 pour un vrai test de scenario historique. Verifie sans effet negatif sur
les modeles existants (tous utilisent des fenetres glissantes, ou beneficient directement de
plus d'historique -- ex. modele_saisonnalite.py, dont la limite documentee "seulement 2 ans"
est resolue par ce changement). Secteurs restes a 2 ans (pas de modele qui en a besoin plus
long pour l'instant, pas d'ingestion excessive sans usage reel).

Meme choix technique que global-macro-desk-cloud : appel direct a l'API chart de Yahoo
(`requests`), pas la librairie `yfinance` -- deja trouve chez eux (audit 2026-08-23) que la
librairie renvoie des donnees tronquees pour certains tickers alors que ce meme endpoint
interroge directement est fiable. Verifie a nouveau ici le 2026-09-08 sur ^VIX et ^GSPC :
fonctionne, frais au jour meme.

Chaque run reecrit l'historique complet (pas d'append incremental) -- evite toute
derive/doublon si un run est manque ou relance.

Usage :
    python ingestion_yfinance_indices.py
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

BRUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "yfinance"
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

INDICES_LONGUE_HISTOIRE = {
    "SP500": "%5EGSPC",
    "VIX": "%5EVIX",
}

SECTEURS = {
    # 10 ETF sectoriels SPDR (S&P 500 decompose par secteur) -- verifies frais le 2026-09-08,
    # utilises par modele_rotation_sectorielle.py (factorielle/). 2 ans (pas 30) -- aucun
    # modele n'a besoin de plus pour l'instant, pas d'ingestion excessive sans usage reel.
    "XLK": "XLK",  # Technologie
    "XLF": "XLF",  # Finance
    "XLE": "XLE",  # Energie
    "XLV": "XLV",  # Sante
    "XLI": "XLI",  # Industrie
    "XLY": "XLY",  # Consommation discretionnaire
    "XLP": "XLP",  # Consommation de base
    "XLU": "XLU",  # Services collectifs
    "XLB": "XLB",  # Materiaux
    "XLRE": "XLRE",  # Immobilier
}

MIN_LIGNES = 5
MAX_JOURS_RETARD = 7  # meme garde-fou que GMDC : un fournisseur peut arreter de mettre a jour
                       # un ticker sans jamais renvoyer d'erreur ni d'historique vide.


def fetch_chart(ticker: str, plage: str) -> list:
    resp = requests.get(
        YAHOO_CHART_URL.format(ticker=ticker),
        params={"range": plage, "interval": "1d"},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    resultats = data.get("chart", {}).get("result")
    if not resultats:
        erreur = data.get("chart", {}).get("error")
        raise ValueError(f"reponse Yahoo sans resultat pour {ticker} -- {erreur}")
    r = resultats[0]
    timestamps = r.get("timestamp") or []
    closes = r.get("indicators", {}).get("quote", [{}])[0].get("close") or []
    out = []
    for ts, close in zip(timestamps, closes):
        if close is None:
            continue
        date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        out.append((date_str, close))
    return out


def valider(points: list, nom: str) -> None:
    if not points:
        raise ValueError(f"aucune donnee renvoyee pour {nom}")
    if len(points) < MIN_LIGNES:
        raise ValueError(f"seulement {len(points)} ligne(s) pour {nom} -- snapshot degrade")
    if any(close <= 0 for _, close in points):
        raise ValueError(f"cloture(s) a zero ou negative pour {nom}")
    derniere_date = datetime.strptime(points[-1][0], "%Y-%m-%d").date()
    retard = (datetime.now(timezone.utc).date() - derniere_date).days
    if retard > MAX_JOURS_RETARD:
        raise ValueError(f"derniere donnee du {derniere_date} pour {nom} -- {retard} jours de "
                          f"retard (seuil {MAX_JOURS_RETARD})")


def main() -> int:
    tous = [(nom, ticker, "30y") for nom, ticker in INDICES_LONGUE_HISTOIRE.items()] + \
        [(nom, ticker, "2y") for nom, ticker in SECTEURS.items()]

    echecs = []
    for nom, ticker, plage in tous:
        try:
            points = fetch_chart(ticker, plage)
            valider(points, nom)
        except (ValueError, requests.RequestException) as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
            continue

        BRUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = BRUT_DIR / f"{nom}.csv"
        with out_path.open("w", encoding="utf-8") as f:
            f.write("date,close\n")
            for date_str, close in points:
                f.write(f"{date_str},{close:.6f}\n")
        print(f"{nom} : {len(points)} lignes -> {out_path}")

    if echecs:
        print(f"\n{len(echecs)}/{len(tous)} indices en echec : {[n for n, _ in echecs]}")
        return 1

    print(f"\nOK -- {len(tous)} indices ingeres")
    return 0


if __name__ == "__main__":
    sys.exit(main())
