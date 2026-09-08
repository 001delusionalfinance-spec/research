"""Ingestion CFTC -- positionnement speculatif (Commitments of Traders), hebdomadaire.

Meme choix technique que global-macro-desk-cloud : API Socrata (publicreporting.cftc.gov,
JSON propre), aucune cle requise.

Univers plus large qu'un desk mono-fonds -- 9 contrats couvrant actions (S&P), taux (UST 10Y),
change (EUR/JPY/GBP + indice dollar), or, petrole, vol (VIX). Chaque nom verifie en direct le
2026-09-08 contre les donnees les plus recentes (report_date > 2026-08-01), pas copie d'une
recherche approximative -- deux noms plausibles se sont reveles perimes a l'usage :
"10-YEAR U.S. TREASURY NOTES - CHICAGO BOARD OF TRADE" et "BRITISH POUND STERLING - CHICAGO
MERCANTILE EXCHANGE" n'ont plus de donnees depuis 2022-02, le nom courant du contrat a change
("UST 10Y NOTE" / "BRITISH POUND", sans "STERLING") sans que CFTC ne le documente ailleurs que
dans les donnees elles-memes.

Seule transformation acceptee (documentee, seule exception a la regle "brut = non
transforme") : noncomm_net = noncomm_long - noncomm_short, calcule a l'ecriture.

Usage :
    python ingestion_cftc.py
"""

import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SOCRATA_BASE = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"

# Noms exacts verifies en direct le 2026-09-08 contre les donnees les plus recentes.
CONTRACTS = {
    "SP500_EMINI": "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE",
    "UST_10Y": "UST 10Y NOTE - CHICAGO BOARD OF TRADE",
    "EUR_FX": "EURO FX - CHICAGO MERCANTILE EXCHANGE",
    "JPY_FX": "JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE",
    "GBP_FX": "BRITISH POUND - CHICAGO MERCANTILE EXCHANGE",
    "USD_INDEX": "USD INDEX - ICE FUTURES U.S.",
    "GOLD": "GOLD - COMMODITY EXCHANGE INC.",
    "WTI_CRUDE": "WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE",
    "VIX_FUT": "VIX FUTURES - CBOE FUTURES EXCHANGE",
    "NASDAQ_MINI": "NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE",  # ajoute 2026-09-08, verifie frais
    "COPPER": "COPPER- #1 - COMMODITY EXCHANGE INC.",  # ajoute 2026-09-08, verifie frais
    "SILVER": "SILVER - COMMODITY EXCHANGE INC.",  # ajoute 2026-09-08, verifie frais
    "PLATINUM": "PLATINUM - NEW YORK MERCANTILE EXCHANGE",  # ajoute 2026-09-08, verifie frais
}

BRUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "cftc"


def fetch_contract(nom_contrat: str) -> list:
    params = {
        "$where": f"market_and_exchange_names='{nom_contrat}'",
        "$order": "report_date_as_yyyy_mm_dd DESC",
        "$limit": "156",  # ~3 ans hebdomadaires
    }
    url = f"{SOCRATA_BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "research/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def write_contract_csv(cle: str, rows: list) -> Path:
    BRUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BRUT_DIR / f"{cle}.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "noncomm_long", "noncomm_short", "noncomm_net", "comm_long",
                     "comm_short", "comm_net", "open_interest", "traders_noncomm_long",
                     "traders_noncomm_short", "traders_total"])
        for r in sorted(rows, key=lambda r: r["report_date_as_yyyy_mm_dd"]):
            long_ = int(r["noncomm_positions_long_all"])
            short_ = int(r["noncomm_positions_short_all"])
            comm_long = int(r["comm_positions_long_all"])
            comm_short = int(r["comm_positions_short_all"])
            date = r["report_date_as_yyyy_mm_dd"][:10]
            w.writerow([date, long_, short_, long_ - short_, comm_long, comm_short,
                        comm_long - comm_short, r["open_interest_all"],
                        r["traders_noncomm_long_all"], r["traders_noncomm_short_all"],
                        r["traders_tot_all"]])
    return out_path


def main() -> int:
    echecs = []
    for cle, nom_contrat in CONTRACTS.items():
        try:
            rows = fetch_contract(nom_contrat)
            if not rows:
                raise ValueError(f"aucune ligne renvoyee pour '{nom_contrat}'")
            out_path = write_contract_csv(cle, rows)
            print(f"{cle} : {len(rows)} semaines -> {out_path}")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as e:
            echecs.append((cle, str(e)))
            print(f"{cle} : echec -- {e}")

    if echecs:
        print(f"\n{len(echecs)}/{len(CONTRACTS)} contrats en echec : {[c for c, _ in echecs]}")
        return 1

    print(f"\nOK -- {len(CONTRACTS)} contrats ingeres")
    return 0


if __name__ == "__main__":
    sys.exit(main())
