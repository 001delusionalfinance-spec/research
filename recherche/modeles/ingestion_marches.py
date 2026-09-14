"""Ingestion marches -- FX, matieres premieres, volatilite et indices non-US.

Complete `ingestion_yfinance_indices.py` (qui couvre S&P 500 / VIX / secteurs US) et
`ingestion_fred.py` (series macro officielles). Meme technique que les deux autres : appel
direct a l'API chart de Yahoo via `requests`, jamais la librairie `yfinance` (deja trouvee
chez GMDC le 2026-08-23 comme renvoyant des donnees tronquees sur certains tickers alors que
ce meme endpoint interroge directement est fiable).

Pourquoi cet univers precis -- couverture d'un desk macro, pas un scan exhaustif :
- **FX** : chaque paire est une comparaison entre deux politiques monetaires, donc l'univers
  FX est structurellement le double de celui des banques centrales. G10 complet + CNY/KRW
  (les deux blocs asiatiques suivis cote FRED).
- **Matieres premieres** : 5 instruments seulement, choisis pour leur role macro et pas pour
  couvrir le complexe -- energie (Brent/WTI/gaz) comme intrant d'inflation, or comme proxy
  taux reels/debasement, cuivre comme proxy de croissance. Les agricoles sont deliberement
  absentes (role macro marginal).
- **Volatilite** : le VIX est deja ingere ailleurs ; ici la vol de taux (MOVE) et la vol de
  la vol (VVIX), qui manquaient completement.
- **Indices non-US** : expression macro par bloc economique, jamais de la selection de titres.

Tickers verifies en direct le 2026-09-14 (fraicheur constatee, pas supposee) -- 24 des 26
candidats testes repondent au jour meme. Deux rejetes, documentes ici pour ne pas les
retenter a l'aveugle :
- `^V2TX` (VSTOXX, vol zone euro) -- HTTP 404 sur l'endpoint chart, pas disponible par cette
  voie. La vol europeenne reste un trou assume ; a rouvrir seulement avec une autre source.
- `^KS11` (KOSPI) -- connexion coupee par le serveur au test initial, comportement transitoire
  et non une absence de donnee : il est conserve dans la liste, et un echec ponctuel sera
  simplement signale comme les autres sans bloquer le reste.

Chaque run reecrit l'historique complet (pas d'append incremental) -- meme choix que les
autres ingestions, evite toute derive/doublon si un run est manque ou relance.

Usage :
    python ingestion_marches.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

BRUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "marches"
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

# Paires G10 -- convention de marche respectee (EUR/GBP/AUD/NZD cotees contre USD, le reste
# coté USD contre la devise), pour que le signe d'une variation garde son sens habituel.
FX = {
    "EURUSD": "EURUSD=X",
    "USDJPY": "USDJPY=X",
    "GBPUSD": "GBPUSD=X",
    "USDCHF": "USDCHF=X",
    "USDCAD": "USDCAD=X",
    "AUDUSD": "AUDUSD=X",
    "NZDUSD": "NZDUSD=X",
    "USDSEK": "USDSEK=X",
    "USDNOK": "USDNOK=X",
    "DXY": "DX-Y.NYB",      # indice dollar
    "USDCNY": "USDCNY=X",   # bloc Chine (suivi cote FRED via IR3TIB01CNM156N)
    "USDKRW": "USDKRW=X",   # bloc Coree
    # Croisements sans dollar, ajoutes le 2026-09-14. Ils isolent une comparaison entre deux
    # politiques monetaires NON americaines : lire BCE contre BOJ via EURUSD et USDJPY fait
    # transiter la vue par le dollar, qui a sa propre dynamique. EURJPY la donne directement.
    "EURJPY": "EURJPY=X",
    "EURGBP": "EURGBP=X",
    "EURCHF": "EURCHF=X",
    "AUDJPY": "AUDJPY=X",   # couple classique de sensibilite au risque
}

MATIERES = {
    "BRENT": "BZ=F",        # intrant inflation, reference mondiale
    "WTI": "CL=F",          # intrant inflation, reference US
    "GAZ_HENRY_HUB": "NG=F",
    "OR": "GC=F",           # proxy taux reels / debasement monetaire
    "CUIVRE": "HG=F",       # proxy croissance industrielle
}

VOLATILITE = {
    "MOVE": "%5EMOVE",      # volatilite implicite des taux US
    "VVIX": "%5EVVIX",      # volatilite de la volatilite actions
    # Ajoutes le 2026-09-14 : la vol n'existait que pour les actions et les taux, alors que
    # les chocs macro passent souvent d'abord par l'energie et l'or.
    "OVX": "%5EOVX",        # volatilite implicite du petrole
    "GVZ": "%5EGVZ",        # volatilite implicite de l'or
    "VXN": "%5EVXN",        # volatilite implicite du Nasdaq (complete le VIX)
    # Vol FX cherchee et non trouvee : les indices de reference (VXY de JPMorgan, EUVIX)
    # ne sont pas exposes par cet endpoint. Trou assume, c'est le dernier de la ligne vol.
}

INDICES_NON_US = {
    "EUROSTOXX50": "%5ESTOXX50E",
    "NIKKEI225": "%5EN225",
    "FTSE100": "%5EFTSE",
    "DAX": "%5EGDAXI",
    "KOSPI": "%5EKS11",
    "HANGSENG": "%5EHSI",
}

# 15 ans : couvre 2015 (franc suisse), 2020 et le cycle de resserrement 2022-2023 -- assez
# pour les modeles de regime et de stress sans ingerer un historique dont aucun modele n'a
# l'usage. Le S&P 500 et le VIX gardent leurs 30 ans dans l'autre fichier (stress-testing
# 2008, besoin reel et documente la-bas).
PLAGE = "15y"

MIN_LIGNES = 5
MAX_JOURS_RETARD = 7  # meme garde-fou que les autres ingestions : un fournisseur peut arreter
                       # de mettre a jour un ticker sans jamais renvoyer d'erreur.


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


def valider(points: list, nom: str, permet_negatif: bool = False) -> None:
    if not points:
        raise ValueError(f"aucune donnee renvoyee pour {nom}")
    if len(points) < MIN_LIGNES:
        raise ValueError(f"seulement {len(points)} ligne(s) pour {nom} -- snapshot degrade")

    non_positifs = [(d, c) for d, c in points if c <= 0]
    if non_positifs and not permet_negatif:
        # Un taux de change, un indice ou une mesure de volatilite ne peut pas etre <= 0 :
        # c'est de la donnee corrompue, pas un evenement de marche.
        raise ValueError(f"cloture(s) a zero ou negative pour {nom}")
    if non_positifs and permet_negatif:
        # Cas reel rencontre au test du 2026-09-14 : le WTI (CL=F) cote -37.63 le 2020-04-20,
        # effondrement authentique du contrat de mai a l'expiration. Rejeter la serie pour ca
        # aurait supprime une matiere premiere centrale a cause d'un evenement qui a vraiment
        # eu lieu. On tolere donc l'isolat, mais pas une serie truffee de negatifs -- qui elle
        # resterait une corruption.
        part = len(non_positifs) / len(points)
        if part > 0.05:
            raise ValueError(f"{len(non_positifs)}/{len(points)} clotures <= 0 pour {nom} "
                             f"({part:.1%}) -- trop nombreuses pour un evenement de marche")
        dates = ", ".join(d for d, _ in non_positifs[:5])
        print(f"  {nom} : {len(non_positifs)} cloture(s) <= 0 conservee(s) ({dates}) -- "
              f"evenement de marche sur contrat a terme, pas une corruption")
    derniere_date = datetime.strptime(points[-1][0], "%Y-%m-%d").date()
    retard = (datetime.now(timezone.utc).date() - derniere_date).days
    if retard > MAX_JOURS_RETARD:
        raise ValueError(f"derniere donnee du {derniere_date} pour {nom} -- {retard} jours de "
                         f"retard (seuil {MAX_JOURS_RETARD})")


def main() -> int:
    tous = []
    for famille, mapping in (("fx", FX), ("matieres", MATIERES),
                             ("volatilite", VOLATILITE), ("indices", INDICES_NON_US)):
        tous += [(famille, nom, ticker) for nom, ticker in mapping.items()]

    echecs, inchanges = [], []
    for famille, nom, ticker in tous:
        try:
            points = fetch_chart(ticker, PLAGE)
            valider(points, nom, permet_negatif=(famille == "matieres"))
        except (ValueError, requests.RequestException) as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
            continue

        dossier = BRUT_DIR / famille
        dossier.mkdir(parents=True, exist_ok=True)
        out_path = dossier / f"{nom}.csv"
        contenu = "date,close\n" + "".join(
            f"{date_str},{close:.6f}\n" for date_str, close in points)

        # Ecriture CONDITIONNELLE. Cette ingestion tourne toutes les 30 minutes et reecrit
        # l'historique complet a chaque passage -- environ 3 Mo pour l'ensemble des marches, soit
        # une trentaine de reecritures par jour ouvre. Or a un instant donne la plupart de ces
        # marches ne cotent pas : les indices asiatiques pendant la seance americaine, les
        # matieres premieres hors de leurs heures. Reecrire un fichier identique cree un objet
        # git nouveau pour rien et fait grossir le depot sans rien apporter.
        if out_path.exists() and out_path.read_text(encoding="utf-8") == contenu:
            inchanges.append(nom)
            continue
        out_path.write_text(contenu, encoding="utf-8")
        print(f"{nom} : {len(points)} lignes -> {out_path}")

    if inchanges:
        print(f"\n{len(inchanges)} marche(s) inchange(s) depuis le passage precedent, fichier "
              f"non reecrit (marche ferme ou aucune cotation nouvelle)")
    if echecs:
        print(f"\n{len(echecs)}/{len(tous)} marches en echec : {[n for n, _ in echecs]}")
        return 1

    print(f"\nOK -- {len(tous)} marches ingeres ({len(tous) - len(inchanges)} mis a jour, "
          f"{len(inchanges)} inchanges)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
