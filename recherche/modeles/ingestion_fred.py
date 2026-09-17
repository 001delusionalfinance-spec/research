"""
Ingestion FRED -- API officielle authentifiee, jamais le endpoint CSV public.

Meme choix que global-macro-desk-cloud, et pour la meme raison verifiee a nouveau ici le
2026-09-08 : `fred.stlouisfed.org/graph/fredgraph.csv` (public, sans cle) a servi a explorer
quelles series existent et sont fraiches avant d'ecrire ce fichier, et s'est deja montre
instable sous une rafale d'appels (une reponse tronquee au milieu d'une requete). L'API
officielle (`api.stlouisfed.org/fred/series/observations`) est le seul chemin retenu pour
l'ingestion planifiee.

ETENDU LE 2026-09-14 -- l'etat decrit juste en dessous est celui du 2026-09-08 et il est
conserve tel quel (pas de reecriture de l'historique) ; ce qui a ete ajoute depuis est
documente bloc par bloc dans la liste SERIES elle-meme. En resume : passage de 5 a 12 blocs
de banques centrales (G10 complet + Chine + Coree), plus la courbe des taux US au complet,
les rendements reels (TIPS), les souverains 10 ans non-US, le credit emergent et la dette
publique US. Memes regles qu'au premier jour : chaque serie testee en direct avant ajout,
chaque rejet documente avec sa raison.

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
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
TENTATIVES = 3

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
    "LRHUTTTTGBM156S",     # Taux de chomage UK, harmonise OCDE (mensuel).
    #     SOUS SURVEILLANCE (2026-09-14) : derniere observation a 166 jours pour
    #     un rythme habituel de 31, quand les autres pays de la meme famille OCDE
    #     sont a 105. Elle decroche donc de ses pairs sans etre gelee.
    #     controle_fraicheur.py la classe SUSPECTE et basculera seul en GELEE si
    #     elle passe le seuil. Deux remplacants (LRUNTTTTGBM156S, LRHUTTTTGBQ156S)
    #     n'ont pas pu etre testes -- l'endpoint public d'exploration de FRED
    #     etait en timeout. A retenter avant de la remplacer : substituer une
    #     serie sans avoir verifie la remplacante serait pire que la garder.
    # --- Japon ---
    "IRSTCI01JPM156N",     # Taux interbancaire au jour le jour, proxy taux BOJ (mensuel)
    "LRHUTTTTJPM156S",     # Taux de chomage Japon, harmonise OCDE (mensuel)
    # --- Chine (aucune serie chomage fiable disponible -- taux seul) ---
    "IR3TIB01CNM156N",     # Taux interbancaire 3 mois, proxy conditions monetaires (mensuel)

    # ======================================================================================
    # Extension du 2026-09-14 -- passage de 5 a 12 blocs de banques centrales (G10 complet +
    # Chine + Coree), plus la courbe US, les rendements reels et les souverains non-US.
    # Chaque serie ci-dessous a ete testee en direct le 2026-09-14 via l'endpoint public
    # (meme methode d'exploration que le 2026-09-08) : seules celles dont la derniere
    # observation etait >= 2026-06-01 ont ete retenues. Les rejets sont documentes en bas.
    # ======================================================================================

    # --- Canada (BOC) ---
    "IRSTCI01CAM156N",     # Taux interbancaire au jour le jour, proxy BOC (mensuel)
    "LRHUTTTTCAM156S",     # Taux de chomage Canada, harmonise OCDE (mensuel)
    # --- Australie (RBA) ---
    "IRSTCI01AUM156N",     # Taux interbancaire au jour le jour, proxy RBA (mensuel)
    "LRHUTTTTAUM156S",     # Taux de chomage Australie, harmonise OCDE (mensuel)
    # --- Norvege (Norges Bank) ---
    "IRSTCI01NOM156N",     # Taux interbancaire au jour le jour, proxy Norges (mensuel)
    "LRHUTTTTNOM156S",     # Taux de chomage Norvege, harmonise OCDE (mensuel)
    # --- Coree (BOK) ---
    "IRSTCI01KRM156N",     # Taux interbancaire au jour le jour, proxy BOK (mensuel)
    "LRHUTTTTKRM156S",     # Taux de chomage Coree, harmonise OCDE (mensuel)
    # --- Suisse (SNB) -- proxy 3 mois, PAS le jour le jour ---
    #     IRSTCI01CHM156N (jour le jour) teste et rejete : gele a 2024-03.
    "IR3TIB01CHM156N",     # Taux interbancaire 3 mois, proxy SNB (mensuel)
    #     Aucun chomage suisse exploitable : LRHUTTTTCHM156S renvoie 404, LMUNRRTTCHM156S
    #     gele a 2023-12. Trou assume, pas un oubli.
    # --- Nouvelle-Zelande (RBNZ) -- proxy 3 mois ---
    #     IRSTCI01NZM156N (jour le jour) teste et rejete : gele a 2024-12.
    "IR3TIB01NZM156N",     # Taux interbancaire 3 mois, proxy RBNZ (mensuel)
    # --- Suede (Riksbank) -- proxy 3 mois ---
    #     IRSTCI01SEM156N (jour le jour) teste et rejete : gele a 2020-10.
    "IR3TIB01SEM156N",     # Taux interbancaire 3 mois, proxy Riksbank (mensuel)
    "LRHUTTTTSEM156S",     # Taux de chomage Suede, harmonise OCDE (mensuel)

    # --- Courbe des taux US : points manquants (quotidiens, frais au 2026-09-10) ---
    "DGS3MO",    # Taux souverain 3 mois -- extremite courte de la courbe
    "DGS5",      # Taux souverain 5 ans -- ventre de la courbe
    "DGS30",     # Taux souverain 30 ans -- extremite longue

    # --- Ajoutees le 2026-09-17 : points courts pour bootstrap de taux forward implicites,
    #     utilises par modele_probabilite_reunion_fed.py (probabilite de mouvement du taux
    #     directeur US par horizon). Testees fraiches en direct via fredgraph.csv avant ajout
    #     (derniere observation 2026-09-15 sur les 3, aucun gel) -- l'API authentifiee reste le
    #     seul chemin retenu pour l'ingestion planifiee, meme regle que le reste de ce fichier.
    "DGS1MO",    # Taux souverain 1 mois -- ancre courte du bootstrap forward
    "DGS6MO",    # Taux souverain 6 mois -- point intermediaire du bootstrap forward
    "DGS1",      # Taux souverain 1 an -- horizon long du bootstrap forward

    # --- Rendements reels US et anticipations d'inflation (quotidiens) ---
    #     Manquaient completement alors que le taux reel est un intrant macro central
    #     (cout reel du capital, proxy de la posture monetaire une fois l'inflation retiree).
    "DFII5",     # Rendement reel 5 ans (TIPS)
    "DFII10",    # Rendement reel 10 ans (TIPS)
    "T10YIE",    # Point mort d'inflation 10 ans (anticipation de marche)

    # --- Souverains 10 ans non-US (mensuels, source OCDE -- frais a 2026-06-01) ---
    #     Frequence mensuelle seulement : suffisant pour du differentiel de taux entre blocs,
    #     insuffisant pour du suivi quotidien. Limite assumee, a remplacer par une source
    #     nationale directe si un modele exige du quotidien hors US.
    "IRLTLT01DEM156N",     # Allemagne 10 ans
    "IRLTLT01GBM156N",     # Royaume-Uni 10 ans
    "IRLTLT01JPM156N",     # Japon 10 ans
    "IRLTLT01CAM156N",     # Canada 10 ans
    "IRLTLT01KRM156N",     # Coree 10 ans

    # --- Credit emergent ---
    "BAMLEMCBPIOAS",       # Spread credit corporate emergent (quotidien)

    # --- Credit europeen et emergent, elargissement du 2026-09-14 ---
    #     Le crediteait couvert pour les seuls US (IG + HY). Un desk macro lit aussi le credit
    #     europeen et le souverain emergent, qui ne bougent pas en phase avec le credit US.
    "BAMLHE00EHYIOAS",       # Spread high-yield europeen (quotidien)
    "BAMLHE00EHYIEY",        # Rendement high-yield europeen (quotidien)
    "BAMLEMHBHYCRPIOAS",     # Spread high-yield emergent
    "BAMLEMPBPUBSICRPIOAS",  # Spread souverain public emergent -- comble l'absence signalee
                             # le matin meme, quand BAMLEMPUBLSLCRPIUSOAS s'etait revele
                             # inexistant sous ce nom.
    "BAMLEMFSFCRPIOAS",      # Spread emetteurs financiers emergents
    "BAMLC0A0CMEY",          # Rendement investment-grade US (complete le spread deja ingere)
    #     BAMLEMPUBLSLCRPIUSOAS (souverain emergent) teste : renvoie 404, n'existe pas sous ce
    #     nom. Le souverain emergent reste absent.

    # --- Budgetaire ---
    #     Seule serie budgetaire retenue. Sa derniere observation (2026-01) est en dehors du
    #     seuil de fraicheur applique aux autres, et c'est normal : serie TRIMESTRIELLE sur une
    #     variable structurelle lente, deux trimestres de retard est le regime normal de
    #     publication, pas un gel. Le seuil >= 2026-06-01 a ete concu pour du mensuel/quotidien.
    "GFDEGDQ188S",         # Dette federale US en % du PIB (trimestriel)
    #     FYFSGDA188S (deficit federal en % du PIB) teste et ECARTE : serie ANNUELLE, derniere
    #     observation 2025-01, soit ~20 mois de retard -- inexploitable pour du suivi. Le
    #     calendrier d'emission souveraine et le deficit courant demandent une autre source
    #     (Treasury direct), chantier non ouvert ici.

    # --- Activite reelle US (ajoute le 2026-09-14, toutes verifiees fraiches) ---
    #     Le repo n'avait AUCUNE mesure d'activite reelle : ni ventes, ni production, ni
    #     enquete. Il ne voyait que les prix, les taux et l'emploi.
    "RSAFS",     # Ventes de detail et restauration (mensuel)
    "INDPRO",    # Production industrielle (mensuel)
    "CFNAI",     # Indice d'activite nationale, Chicago Fed (mensuel, 85 indicateurs agreges)
    "UMCSENT",   # Confiance des consommateurs, Michigan (mensuel)

    # --- Substituts gratuits du PMI (enquetes manufacturieres des Fed regionales) ---
    #     Les PMI S&P Global et l'ISM sont proprietaires et payants : aucune voie gratuite
    #     trouvee. Les enquetes des Fed regionales mesurent la meme chose (diffusion de
    #     l'activite manufacturiere declaree par les entreprises), sont publiques, et sortent
    #     AVANT l'ISM dans le mois -- ce sont les substituts retenus, pas un pis-aller cache.
    "GACDISA066MSFRBNY",   # Enquete manufacturiere Fed de New York (Empire State)
    "GACDFSA066MSFRBPHI",  # Enquete manufacturiere Fed de Philadelphie

    # --- Agregats monetaires US ---
    "TOTRESNS",  # Reserves des banques aupres de la Fed (mensuel) -- liquidite du systeme
    "BOGMBASE",  # Base monetaire (mensuel)
    "WRESBAL",   # Reserves bancaires, HEBDOMADAIRE -- meme grandeur que TOTRESNS mais en
                 # frequence utile pour suivre la liquidite ; les deux sont gardees.
    "RESPPLLOPNWW",  # Prets de la Fed aux etablissements (hebdomadaire)

    # --- Exterieur et budgetaire (ajoute le 2026-09-14) ---
    "IEABC",         # Solde du compte courant US (trimestriel)
    "MTSDS133FMS",   # Deficit/excedent budgetaire MENSUEL du Tresor US.
                     # Remplace fonctionnellement FYFSGDA188S, ecartee le meme jour parce
                     # qu'annuelle et vieille de ~20 mois : celle-ci est mensuelle et fraiche.
    "TRESEGUSM052N",  # Reserves internationales des US (mensuel)
    #     BOPBCA (compte courant, ancienne serie) testee et rejetee : figee a 2014-01.
    #     TOTRESV testee : renvoie 404, n'existe pas sous ce nom.

    # ======================================================================================
    # BILANS DE BANQUES CENTRALES -- QE / QT (ajoute le 2026-09-14)
    #
    # Trou majeur jusqu'ici : le repo suivait les TAUX DIRECTEURS des 12 blocs mais AUCUN
    # bilan. Or l'assouplissement et le resserrement quantitatifs agissent sur les taux longs
    # et la liquidite independamment du taux directeur -- une banque centrale peut tenir son
    # taux inchange et durcir fortement en laissant son bilan se reduire. Sans ces series, le
    # dispositif ne voyait qu'une moitie de la politique monetaire.
    # ======================================================================================

    # --- Reserve federale (hebdomadaire, source H.4.1) ---
    "WALCL",     # Actif total de la Fed -- la mesure de reference du QE/QT
    "TREAST",    # Titres du Tresor detenus par la Fed
    "WSHOMCB",   # Titres hypothecaires (MBS) detenus par la Fed
    "WSHOSHO",   # Titres detenus outright (portefeuille SOMA)
    "WLRRAL",    # Reverse repo total -- liquidite retiree du systeme
    "RRPONTSYD",  # Reverse repo overnight, QUOTIDIEN -- le drain de liquidite le plus reactif
    "WTREGEN",   # Compte general du Tresor a la Fed, vu depuis le bilan de la Fed.
                 # Recoupe volontairement `solde_tresorerie` d'ingestion_tresor_us.py (vu,
                 # lui, depuis le Tresor et en quotidien) : les avoir tous deux issus du
                 # meme releve H.4.1 que WALCL et WLRRAL permet de calculer proprement la
                 # liquidite nette (actif total moins compte du Tresor moins reverse repo)
                 # sans melanger des sources aux dates de publication differentes.

    # --- Autres banques centrales ---
    "ECBASSETSW",  # Actif total de la BCE (hebdomadaire)
    "JPNASSETS",   # Actif total de la Banque du Japon (mensuel)
    #     CHNASSETS (PBOC) et SWSTOTASSETS (SNB) testees : renvoient 404, n'existent pas sous
    #     ces identifiants. Bilans PBOC et SNB toujours absents.
    #     Bilan de la Banque d'Angleterre : pas cherche sur FRED, a prendre chez elle.
    #     H41RESPPALDKNWW (prets d'urgence Fed) testee et ecartee : figee a 2026-05, serie
    #     dormante hors periode de stress -- son gel n'est pas un incident, mais elle
    #     declencherait le detecteur de peremption pour rien.
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

    # Reessai sur erreur TRANSITOIRE uniquement. Defaut reel constate en CI le 2026-09-14 :
    # l'API FRED a renvoye un HTTP 500 sur une seule serie (chomage Coree) parmi 58, et comme
    # il n'y avait aucun reessai, cet incident serveur isole faisait echouer toute l'etape
    # d'ingestion. Un 4xx (identifiant invalide, cle refusee) n'est PAS reessaye : il ne
    # deviendra pas valide en insistant, et le masquer retarderait le vrai diagnostic.
    for essai in range(TENTATIVES):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code < 500 or essai == TENTATIVES - 1:
                raise
            time.sleep(2 * (essai + 1))
        except (urllib.error.URLError, TimeoutError):
            if essai == TENTATIVES - 1:
                raise
            time.sleep(2 * (essai + 1))
    raise RuntimeError(f"{series_id} : sortie de boucle de reessai sans resultat")


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
