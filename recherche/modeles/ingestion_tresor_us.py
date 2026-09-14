"""Ingestion Tresor americain -- API FiscalData (data.treasury.gov, officielle, sans cle).

Comble le **calendrier d'emission souveraine**, absent jusqu'au 2026-09-14, et deux variables
de liquidite qui n'existaient nulle part dans le repo.

Trois jeux, chacun pour une raison macro precise :

1. **Adjudications (`auctions_query`)** -- le calendrier d'emission lui-meme : quel titre,
   quelle maturite, quel montant, quelle date. C'est l'offre de papier souverain. Une hausse
   d'emission sur le long terme pese sur la prime de terme independamment de toute decision
   de banque centrale -- c'est precisement ce qu'un dispositif centre sur la Fed ne voit pas.
   Particularite : ce jeu contient des dates **futures** (adjudications annoncees, pas encore
   tenues). C'est voulu et c'est tout l'interet d'un calendrier. Le controle de peremption
   porte donc sur `record_date`, pas sur `auction_date`.

2. **Dette au jour le jour (`debt_to_penny`)** -- encours total, part detenue par le public
   et part intra-gouvernementale, en frequence quotidienne. Complete `GFDEGDQ188S` (dette en
   % du PIB, trimestriel) deja ingere cote FRED : ici c'est le niveau brut, tous les jours.

3. **Solde du compte de tresorerie (`operating_cash_balance`)** -- le compte du Tresor a la
   Fed. Variable de liquidite de premier ordre et souvent ignoree : quand ce compte se
   remplit, il retire des reserves du systeme bancaire ; quand il se vide, il en injecte.
   Un mouvement de plusieurs centaines de milliards deplace la liquidite sans qu'aucune
   decision de politique monetaire n'ait ete prise.

L'API pagine et trie cote serveur (`sort=-record_date`), on ne recupere donc que la fenetre
demandee, pas tout l'historique a chaque run.

Usage :
    python ingestion_tresor_us.py
"""

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
BRUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "tresor_us"

# (nom de sortie, chemin API, champs retenus, retard max en jours, libelle)
JEUX = [
    ("adjudications",
     "/v1/accounting/od/auctions_query?sort=-auction_date&page[size]=400",
     ["record_date", "auction_date", "issue_date", "maturity_date", "security_type",
      "security_term", "offering_amt", "high_yield", "bid_to_cover_ratio"],
     20, "Adjudications du Tresor (calendrier d'emission)"),
    ("dette_quotidienne",
     "/v2/accounting/od/debt_to_penny?sort=-record_date&page[size]=2000",
     ["record_date", "tot_pub_debt_out_amt", "debt_held_public_amt", "intragov_hold_amt"],
     10, "Encours de dette au jour le jour"),
    ("solde_tresorerie",
     "/v1/accounting/dts/operating_cash_balance?sort=-record_date&page[size]=2000",
     ["record_date", "account_type", "close_today_bal", "open_today_bal"],
     10, "Solde du compte de tresorerie a la Fed"),
]

MIN_LIGNES = 20


def fetch(chemin: str) -> list:
    req = urllib.request.Request(BASE + chemin,
                                 headers={"User-Agent": "research/1.0",
                                          "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        charge = json.loads(resp.read().decode("utf-8"))
    lignes = charge.get("data")
    if lignes is None:
        raise ValueError("reponse FiscalData sans bloc 'data'")
    return lignes


def valider(lignes: list, nom: str, retard_max: int) -> None:
    if len(lignes) < MIN_LIGNES:
        raise ValueError(f"seulement {len(lignes)} ligne(s) pour {nom} -- snapshot degrade")
    # `record_date` est la date de PUBLICATION de l'enregistrement. Pour les adjudications,
    # `auction_date` peut etre dans le futur (adjudication annoncee) : mesurer la peremption
    # dessus donnerait un retard negatif et ne detecterait jamais un arret de publication.
    dates = sorted(l["record_date"] for l in lignes if l.get("record_date"))
    if not dates:
        raise ValueError(f"aucune date de publication exploitable pour {nom}")
    derniere = datetime.strptime(dates[-1], "%Y-%m-%d").date()
    retard = (datetime.now(timezone.utc).date() - derniere).days
    if retard > retard_max:
        raise ValueError(f"derniere publication du {dates[-1]} pour {nom} -- {retard} jours "
                         f"de retard (seuil {retard_max})")


def ecrire(nom: str, champs: list, lignes: list) -> Path:
    BRUT_DIR.mkdir(parents=True, exist_ok=True)
    chemin = BRUT_DIR / f"{nom}.csv"
    with chemin.open("w", newline="", encoding="utf-8") as f:
        f.write(",".join(champs) + "\n")
        for ligne in sorted(lignes, key=lambda l: l.get("record_date") or ""):
            valeurs = []
            for champ in champs:
                brut = str(ligne.get(champ, "") or "")
                valeurs.append(f'"{brut}"' if "," in brut else brut)
            f.write(",".join(valeurs) + "\n")
    return chemin


def main() -> int:
    echecs = []
    for nom, chemin_api, champs, retard_max, libelle in JEUX:
        try:
            lignes = fetch(chemin_api)
            valider(lignes, libelle, retard_max)
        except (ValueError, KeyError, urllib.error.URLError,
                urllib.error.HTTPError, TimeoutError) as e:
            echecs.append((nom, str(e)))
            print(f"{libelle} : echec -- {e}")
            continue
        sortie = ecrire(nom, champs, lignes)
        print(f"{libelle} : {len(lignes)} lignes -> {sortie}")

    if echecs:
        print(f"\n{len(echecs)}/{len(JEUX)} jeux en echec : {[n for n, _ in echecs]}")
        return 1
    print(f"\nOK -- {len(JEUX)} jeux du Tresor US ingeres")
    return 0


if __name__ == "__main__":
    sys.exit(main())
