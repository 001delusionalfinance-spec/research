"""Ingestion yfinance -- indices de reference (S&P 500, VIX), historique 1 an.

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

INDICES = {
    "SP500": "%5EGSPC",
    "VIX": "%5EVIX",
}

MIN_LIGNES = 5
MAX_JOURS_RETARD = 7  # meme garde-fou que GMDC : un fournisseur peut arreter de mettre a jour
                       # un ticker sans jamais renvoyer d'erreur ni d'historique vide.


def fetch_chart(ticker: str) -> list:
    resp = requests.get(
        YAHOO_CHART_URL.format(ticker=ticker),
        params={"range": "1y", "interval": "1d"},
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
    echecs = []
    for nom, ticker in INDICES.items():
        try:
            points = fetch_chart(ticker)
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
        print(f"\n{len(echecs)}/{len(INDICES)} indices en echec : {[n for n, _ in echecs]}")
        return 1

    print(f"\nOK -- {len(INDICES)} indices ingeres")
    return 0


if __name__ == "__main__":
    sys.exit(main())
