"""
Ingestion FRED -- API officielle authentifiee, jamais le endpoint CSV public.

Meme choix que global-macro-desk-cloud, et pour la meme raison verifiee a nouveau ici le
2026-09-08 : `fred.stlouisfed.org/graph/fredgraph.csv` (public, sans cle) a servi a explorer
quelles series existent et sont fraiches avant d'ecrire ce fichier, et s'est deja montre
instable sous une rafale d'appels (une reponse tronquee au milieu d'une requete). L'API
officielle (`api.stlouisfed.org/fred/series/observations`) est le seul chemin retenu pour
l'ingestion planifiee.

Liste de series verifiee en direct le 2026-09-08 (fraicheur reelle constatee, pas supposee) --
5 blocs economiques (US / Zone euro / UK / Japon / Chine), deux dimensions seulement :

- Taux directeur (ou proxy le plus proche disponible en frequence utile) -- fraicheur bonne a
  excellente partout.
- Emploi (taux de chomage, ou proxy allemand pour la zone euro -- l'agregat officiel a un
  retard de plusieurs mois) -- fraicheur bonne partout SAUF Chine (aucune serie chomage fiable
  trouvee sur FRED, testee et rejetee : LRHUTTTTCNM156S n'existe pas).

**CPI/inflation deliberement absente de cette liste pour les blocs hors US** -- teste et
rejete pour chacun, pas un oubli : Allemagne (CPHPTT01DEM659N) figee a 2025-04, Royaume-Uni
(CPHPTT01GBM659N) figee a 2025-03, Japon (CPALTT01JPM659N, JPNCPICORMINMEI) figees toutes
les deux a 2021-06, Chine (CPALTT01CNM659N) figee a 2025-04. Les series CPI internationales
disponibles gratuitement sur FRED (source OCDE) ont couramment 12 a 60+ mois de retard --
une contrainte de source reelle, pas un choix arbitraire. CPIAUCSL (US, mensuel, ~1 mois de
retard) est la seule serie d'inflation retenue ici. Revisiter si une source alternative
(direct Eurostat/ONS/e-Stat/NBS) est un jour jugee utile.

Usage :
    python ingestion_fred.py
    (lit FRED_API_KEY depuis l'environnement -- jamais en argument, jamais en dur)
"""

import csv
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

SERIES = [
    # --- US ---
    "DFF",       # Fed funds effective rate (quotidien)
    "UNRATE",    # Taux de chomage (mensuel)
    "CPIAUCSL",  # CPI, tous postes (mensuel)
    "DGS10",     # Taux souverain 10 ans (quotidien) -- courbe des taux, verifie frais 2026-09-08
    "DGS2",      # Taux souverain 2 ans (quotidien) -- courbe des taux
    "TOTBKCR",   # Credit bancaire total (hebdo) -- cycle du credit, verifie frais 2026-09-08
    "RBUSBIS",   # Taux de change effectif reel US, BIS (mensuel) -- verifie frais 2026-09-08
    "HOUST",     # Mises en chantier logements (mensuel) -- cycle immobilier
    "MORTGAGE30US",  # Taux hypothecaire fixe 30 ans (hebdo) -- cycle immobilier
    "PERMIT",    # Permis de construire (mensuel) -- cycle immobilier
    "BAMLH0A0HYM2",  # Spread credit high-yield US (quotidien) -- facteur qualite credit
    "BAMLC0A0CM",    # Spread credit investment-grade US (quotidien) -- facteur qualite credit
    "BOPGSTB",       # Balance commerciale biens+services US (mensuel) -- verifie frais 2026-09-08
    # --- Zone euro (BCE + Allemagne comme proxy emploi -- l'agregat zone euro officiel a
    #     plusieurs mois de retard, l'Allemagne est fraiche et pese ~29% du PIB de la zone) ---
    "ECBDFR",             # Taux de la facilite de depot BCE (quotidien)
    "LRHUTTTTDEM156S",    # Taux de chomage Allemagne, harmonise OCDE (mensuel)
    # --- Royaume-Uni ---
    "IUDSOIA",             # SONIA, taux au jour le jour (quotidien)
    "LRHUTTTTGBM156S",     # Taux de chomage UK, harmonise OCDE (mensuel)
    # --- Japon ---
    "IRSTCI01JPM156N",     # Taux interbancaire au jour le jour, proxy taux BOJ (mensuel)
    "LRHUTTTTJPM156S",     # Taux de chomage Japon, harmonise OCDE (mensuel)
    # --- Chine (aucune serie chomage fiable disponible -- taux seul) ---
    "IR3TIB01CNM156N",     # Taux interbancaire 3 mois, proxy conditions monetaires (mensuel)
]

BRUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "fred"


def fetch_series(series_id: str, api_key: str) -> dict:
    # limit=100 -- bug reel trouve le 2026-09-08 : suffisant pour les series mensuelles/
    # trimestrielles (~8 ans d'historique), mais beaucoup trop court pour les series
    # quotidiennes (DFF, DGS10, DGS2, ECBDFR, IUDSOIA, BAMLH0A0HYM2, BAMLC0A0CM -- ~100 jours
    # ouvres = ~5 mois). Comme write_series_csv() ECRASE le fichier a chaque ingestion (pas
    # d'accumulation, cf. accumuler_csv() dans _lib.py qui elle accumule), cette fenetre ne
    # grandit jamais dans le temps -- casse modele_momentum_credit.py (besoin de 365j),
    # modele_hp_filter_taux.py (besoin de >=100 points valides, echoue meme a exactement 100
    # bruts des que quelques jours feries FRED (valeur ".") sont filtres) et
    # modele_pca_taux.py (besoin de dates communes entre blocs quotidiens et mensuels -- une
    # fenetre quotidienne de 5 mois ne contient que 4-5 debuts de mois exploitables). Releve a
    # 3000 (~12 ans ouvres) : couvre large marge pour toutes les series quotidiennes, sans cout
    # pour les series mensuelles/trimestrielles (FRED renvoie simplement tout l'historique
    # disponible si celui-ci est plus court que la limite demandee).
    params = f"series_id={series_id}&api_key={api_key}&file_type=json&sort_order=desc&limit=3000"
    url = f"{FRED_BASE}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "research/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def write_series_csv(series_id: str, payload: dict) -> Path:
    BRUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BRUT_DIR / f"{series_id}.csv"
    observations = payload.get("observations", [])
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "value"])
        for obs in sorted(observations, key=lambda o: o["date"]):
            writer.writerow([obs["date"], obs["value"]])
    return out_path


def main() -> int:
    api_key = (os.environ.get("FRED_API_KEY") or "").strip()  # bug reel trouve en CI le
        # 2026-09-08 : la valeur du secret GitHub contenait un espace en fin de chaine (ajoute
        # au moment de coller la valeur dans le prompt gh secret set), cassant l'URL avec
        # "InvalidURL: URL can't contain control characters" -- strip() defensif, pas une
        # tolerance a une cle invalide (le controle suivant leve toujours si vide apres strip)
    if not api_key:
        print("FRED_API_KEY absente de l'environnement -- rien a faire, echec explicite.")
        return 1

    echecs = []
    for series_id in SERIES:
        try:
            payload = fetch_series(series_id, api_key)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            echecs.append((series_id, str(e)))
            print(f"{series_id} : echec -- {e}")
            continue

        out_path = write_series_csv(series_id, payload)
        n = len(payload.get("observations", []))
        print(f"{series_id} : {n} observations -> {out_path}")

    if echecs:
        print(f"\n{len(echecs)}/{len(SERIES)} series en echec : {[s for s, _ in echecs]}")
        return 1

    print(f"\nOK -- {len(SERIES)} series ingerees, {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC")
    return 0


if __name__ == "__main__":
    sys.exit(main())
