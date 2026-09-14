"""Ingestion BIS -- taux directeurs quotidiens et ratios de service de la dette.

Deux ajouts du 2026-09-14, tous deux verifies en direct avant ecriture.

**1. Taux directeurs (`WS_CBPOL`), quotidiens, 12 blocs.**
`ingestion_fred.py` couvre les banques centrales par des **proxies interbancaires mensuels**
(IRSTCI01.., IR3TIB01..) -- c'etait le mieux disponible sur FRED, mais ce sont des taux de
marche, pas la decision de politique monetaire, et en frequence mensuelle. Le BIS publie le
**taux directeur lui-meme, en quotidien** (verifie frais au 2026-09-03/08 selon le pays).

Les deux sont conserves, ils ne mesurent pas la meme chose :
- `WS_CBPOL` = la decision de la banque centrale (ce qu'elle fixe) -> source de reference.
- proxies FRED = les conditions monetaires effectives sur le marche interbancaire, qui
  peuvent s'ecarter du taux directeur (c'est justement l'ecart qui est informatif).

**2. Ratio de service de la dette (`WS_DSR`), trimestriel.**
Part du revenu consacree au service de la dette du secteur prive non financier. C'est l'un
des indicateurs centraux du template de cycle de dette (la charge reelle, pas le stock) --
le stock seul ne dit pas si la dette est soutenable, le service si. Complete `GFDEGDQ188S`
(dette publique US en % du PIB) deja ingere cote FRED, qui lui ne couvre que le public US.

La couverture pays du DSR est plus etroite que celle du CPI et n'est pas documentee
uniformement : les pays absents renvoient HTTP 404 et sont signales comme echecs isoles,
sans interrompre le reste (meme discipline que partout ailleurs dans ce repo).

Note d'implementation : la logique d'appel BIS est volontairement dupliquee depuis
`ingestion_bis_cpi.py` plutot que factorisee dans `_lib.py`. `_lib.py` est importe par les
96 modeles ; y toucher pour une economie de ~25 lignes ferait porter un risque sans rapport
a tout le dispositif.

Usage :
    python ingestion_bis_macro.py
"""

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BRUT_DIR = Path(__file__).resolve().parents[2] / "donnees" / "brut" / "bis"
BIS_BASE = "https://stats.bis.org/api/v2/data/dataflow/BIS/{flow}/1.0/{cle}"
ACCEPT_SDMX = "application/vnd.sdmx.data+json;version=1.0.0"
TENTATIVES = 4

# --- Taux directeurs quotidiens : cle = D.<pays>, verifies un par un le 2026-09-14 ---
TAUX_DIRECTEURS = {
    "US": "Etats-Unis", "XM": "Zone euro", "GB": "Royaume-Uni", "JP": "Japon",
    "CH": "Suisse", "CA": "Canada", "AU": "Australie", "NZ": "Nouvelle-Zelande",
    "SE": "Suede", "NO": "Norvege", "KR": "Coree", "CN": "Chine",
}
# Un taux directeur ne bouge qu'aux reunions, mais la serie est publiee en quotidien.
# Calibre a 35 jours apres mesure : un premier seuil a 15 jours rejetait la COREE, dont la
# derniere observation etait au 2026-08-28 (17 jours) alors que les 10 autres pays etaient a
# J-6. Ce n'est pas un gel, c'est une cadence d'alimentation plus lente cote BIS pour ce pays.
# 35 jours laisse passer ce rythme tout en attrapant un vrai arret de publication.
RETARD_MAX_TAUX = 35

# --- Ratio de service de la dette, secteur prive non financier : cle = Q.<pays>.P ---
# Couverture BIS plus etroite que le CPI. Zone euro (XM) testee et absente (404) : le DSR est
# publie pays par pays, pas en agregat de zone. Les pays ci-dessous incluent des candidats non
# confirmes -- un 404 sera signale comme echec isole, ce qui documente la couverture reelle.
SERVICE_DETTE = {
    "US": "Etats-Unis", "GB": "Royaume-Uni", "JP": "Japon", "CA": "Canada",
    "AU": "Australie", "SE": "Suede", "NO": "Norvege", "KR": "Coree",
    "DE": "Allemagne", "FR": "France", "IT": "Italie", "ES": "Espagne",
}
# Trimestriel et publie avec un decalage important. Mesure du 2026-09-14 : les DOUZE pays
# renvoient exactement 2025-Q4, soit 348 jours depuis le debut du trimestre. Douze pays
# alignes sur la meme periode, ce n'est pas douze gels -- c'est la frontiere de publication
# du jeu de donnees lui-meme. Un premier seuil a 300 jours rejetait donc la totalite du jeu.
# Calibre a 400. Repere pour une relecture future : si la frontiere n'a pas avance au-dela de
# 2025-Q4 dans plusieurs mois, ALORS il s'agira d'un vrai abandon du jeu de donnees.
RETARD_MAX_DSR = 400


def fetch_bis(flow: str, cle: str) -> list:
    """Renvoie [(periode, valeur)] triee. Leve en cas d'echec definitif."""
    url = BIS_BASE.format(flow=flow, cle=cle)
    for essai in range(TENTATIVES):
        try:
            # Les series quotidiennes de taux directeurs sont volumineuses (jusqu'a ~25 000
            # observations) : les Etats-Unis ont depasse un timeout de 45 s au test initial.
            req = urllib.request.Request(
                url, headers={"User-Agent": "research/1.0", "Accept": ACCEPT_SDMX})
            with urllib.request.urlopen(req, timeout=90) as resp:
                charge = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:      # couverture absente : inutile de reessayer
                raise
            if essai == TENTATIVES - 1:
                raise
            time.sleep(2 * (essai + 1))
        except (urllib.error.URLError, TimeoutError):
            if essai == TENTATIVES - 1:
                raise
            time.sleep(2 * (essai + 1))

    data = charge.get("data")
    if not data:
        raise ValueError(f"reponse BIS sans bloc 'data' ({flow}/{cle})")
    periodes = data["structure"]["dimensions"]["observation"][0]["values"]
    series = data["dataSets"][0].get("series") or {}
    if not series:
        raise ValueError(f"aucune serie ({flow}/{cle})")
    observations = list(series.values())[0]["observations"]

    points = []
    for index_str, valeurs in observations.items():
        brut = valeurs[0]
        if brut is None or brut == "":
            continue
        points.append((periodes[int(index_str)]["id"], float(brut)))
    points.sort(key=lambda p: p[0])
    return points


def _date_de_periode(periode: str):
    """'2026-09-08' -> date ; '2025-Q4' -> premier jour du trimestre."""
    if "-Q" in periode:
        annee, trimestre = periode.split("-Q")
        return datetime(int(annee), (int(trimestre) - 1) * 3 + 1, 1, tzinfo=timezone.utc).date()
    morceaux = periode.split("-")
    if len(morceaux) == 2:
        return datetime(int(morceaux[0]), int(morceaux[1]), 1, tzinfo=timezone.utc).date()
    return datetime.strptime(periode, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()


def valider(points: list, nom: str, retard_max: int) -> None:
    if not points:
        raise ValueError(f"aucune donnee pour {nom}")
    if len(points) < 12:
        raise ValueError(f"seulement {len(points)} ligne(s) pour {nom} -- snapshot degrade")
    # Un taux directeur PEUT etre nul ou negatif (Suisse a 0 et Japon en negatif l'ont ete
    # pendant des annees) : aucun controle de signe ici, ce serait une erreur de modele.
    retard = (datetime.now(timezone.utc).date() - _date_de_periode(points[-1][0])).days
    if retard > retard_max:
        raise ValueError(f"derniere observation {points[-1][0]} pour {nom} -- {retard} jours "
                         f"de retard (seuil {retard_max}) : serie probablement gelee")


def ingerer(flow: str, motif_cle: str, pays: dict, sous_dossier: str,
            retard_max: int, entete: str) -> list:
    echecs = []
    dossier = BRUT_DIR / sous_dossier
    for code, nom in pays.items():
        try:
            points = fetch_bis(flow, motif_cle.format(code=code))
            valider(points, nom, retard_max)
        except urllib.error.HTTPError as e:
            echecs.append((nom, f"HTTP {e.code}"))
            print(f"{nom} : echec -- HTTP {e.code} (couverture absente pour ce pays)")
            time.sleep(0.9)
            continue
        except (ValueError, urllib.error.URLError, TimeoutError) as e:
            echecs.append((nom, str(e)))
            print(f"{nom} : echec -- {e}")
            time.sleep(0.9)
            continue

        dossier.mkdir(parents=True, exist_ok=True)
        out_path = dossier / f"{code}.csv"
        with out_path.open("w", encoding="utf-8") as f:
            f.write(f"date,{entete}\n")
            for periode, valeur in points:
                f.write(f"{periode},{valeur:.6f}\n")
        print(f"{nom} : {len(points)} observations (jusqu'a {points[-1][0]}) -> {out_path}")
        time.sleep(0.9)  # l'API BIS coupe sous rafale, constate au test du 2026-09-14
    return echecs


def main() -> int:
    print("=== Taux directeurs (WS_CBPOL, quotidien) ===")
    echecs_taux = ingerer("WS_CBPOL", "D.{code}", TAUX_DIRECTEURS,
                          "taux_directeurs", RETARD_MAX_TAUX, "taux")

    print("\n=== Ratio de service de la dette (WS_DSR, trimestriel) ===")
    echecs_dsr = ingerer("WS_DSR", "Q.{code}.P", SERVICE_DETTE,
                         "service_dette", RETARD_MAX_DSR, "ratio")

    total = len(TAUX_DIRECTEURS) + len(SERVICE_DETTE)
    echecs = echecs_taux + echecs_dsr
    if echecs_taux:
        # Un taux directeur manquant est un vrai probleme : la couverture est verifiee.
        print(f"\n{len(echecs_taux)}/{len(TAUX_DIRECTEURS)} taux directeurs en echec : "
              f"{[n for n, _ in echecs_taux]}")
        return 1
    if echecs_dsr:
        # Un DSR manquant documente seulement la couverture BIS, ce n'est pas une panne.
        print(f"\n{len(echecs_dsr)}/{len(SERVICE_DETTE)} pays sans ratio de service de la "
              f"dette (couverture BIS) : {[n for n, _ in echecs_dsr]}")
    print(f"\nOK -- {total - len(echecs)}/{total} series BIS macro ingerees")
    return 0


if __name__ == "__main__":
    sys.exit(main())
