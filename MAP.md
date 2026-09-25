# MAP — repère du dispositif

Ce fichier décrit l'architecture pour les mainteneurs. Pour lire les résultats, le point
d'entrée unique est [`rapports/README.md`](rapports/README.md).

## Ce que c'est, ce que ce n'est pas

Hub de recherche macroéconomique **complètement séparé** du fonds souverain
(`global-macro-desk-cloud`, mécanique, zéro décision liée à ici). **Uniquement de la
recherche** — comprendre où en est l'économie mondiale et comment ça se voit dans les prix.
Pas de thèse de trade, pas d'exécution, pas de comptabilité, pas de capital engagé, ici ou
ailleurs.

## Ce qui est recherché (le "quoi")

Deux niveaux, jamais confondus :

**Contexte macro, par bloc économique** — où en est le monde, sans opinion :
croissance (PIB, PMI/ISM, emploi), inflation (CPI/PCE, anticipations), politique monétaire
(taux directeurs, bilan des banques centrales, forward guidance), crédit (spreads,
conditions de prêt), commerce extérieur/change, positionnement (COT, flux).
Régions : US, Zone Euro, UK, Japon, Chine, Émergents (agrégé).

**Cross-asset** — comment ce contexte se voit dans les prix : taux (courbe, réel vs
nominal), change, matières premières (énergie, métaux, agri), crédit, volatilité
(actions/taux/change), corrélations et rotations inter-marchés.

## Comment c'est recherché (le "comment") — 8 familles, même taxonomie que le Q1/Q2 déjà
## validé pendant la refonte de GMDC (2026-09-05), appliquée ici sans restriction cette fois

1. **Macro** — régimes croissance/inflation par bloc, cycle de politique monétaire, courbes de
   taux. (`recherche/modeles/macro/`)
2. **Statistique** — corrélations avec test de significativité, cointégration, garde-fou
   multiple-testing (Bonferroni). (`recherche/modeles/statistique/`)
3. **Séries temporelles** — regime-switching (HMM/Kalman), volatilité conditionnelle (GARCH),
   saisonnalité. (`recherche/modeles/series-temporelles/`)
4. **Factorielle** — exposition value/momentum/carry/quality, cross-asset.
   (`recherche/modeles/factorielle/`)
5. **Risque** — tail risk/jump detection, CoVaR, scénarios de drawdown.
   (`recherche/modeles/risque/`)
6. **Positionnement & comportemental** — COT, sentiment, crowding, information mutuelle.
   (`recherche/modeles/positionnement-comportemental/`)
7. **NLP** — discours de banques centrales, minutes FOMC/BCE, texte réglementaire.
   (`recherche/modeles/nlp/`)
8. **ML** — walk-forward strict, même discipline anti-overfitting déjà démontrée dans GMDC
   (un modèle qui ne bat pas la baseline se documente honnêtement, ne se cache pas).
   (`recherche/modeles/ml/`)

Chaque famille produit une lecture, jamais une décision — comprendre le mécanisme, pas
construire un signal de trade.

## Comment c'est automatisé

Chaîne unique : ingestion → modèles → `rapports/donnees/` → publication thématique. Les
graphiques ne sont ajoutés que lorsqu'ils rendent une évolution ou une comparaison plus lisible.

- **Ingestion programmée** (`donnees/brut/`), 1×/jour ouvré :
  - `ingestion_fred.py` — séries officielles, dont les **bilans de banques centrales
    (QE/QT)** : actif total de la Fed et ses composantes (Treasuries, MBS, SOMA), reverse repo
    total et overnight, compte du Trésor vu du bilan de la Fed, plus les actifs totaux de la
    BCE et de la Banque du Japon. Sans ces séries le dispositif ne voyait qu'une moitié de la
    politique monétaire — une banque centrale peut tenir son taux inchangé et durcir
    fortement en laissant son bilan se réduire. 12 blocs de banques centrales (G10 complet +
    Chine + Corée) en taux directeur et emploi, courbe des taux US (3M/2a/5a/10a/30a),
    rendements réels TIPS + point mort d'inflation, souverains 10 ans non-US, spreads crédit
    IG/HY US et corporate émergent, cycle immobilier, balance commerciale, dette publique.
  - `ingestion_marches.py` — FX G10 + DXY + CNY/KRW, 5 matières premières
    (Brent, WTI, gaz, or, cuivre), vol de taux (MOVE) et vol de la vol (VVIX), indices
    non-US (Euro Stoxx, Nikkei, FTSE, DAX, KOSPI, Hang Seng).
  - `ingestion_yfinance_indices.py` — S&P 500 et VIX (30 ans) + 10 ETF sectoriels.
  - `ingestion_bis_cpi.py` — indices de prix à la consommation, **12 blocs** (BIS SDMX).
    C'est ce qui comble le trou « inflation hors US » : FRED, Eurostat, la BCE, l'OCDE et le
    FMI ont tous été testés le 2026-09-14 et étaient trop en retard (de 9 à 60 mois) ; le BIS
    publie à 2026-07. Tableau comparatif des sources dans le docstring du fichier.
  - `ingestion_tresor_us.py` — API FiscalData du Trésor : calendrier d'adjudications (l'offre
    de papier souverain, qui pèse sur la prime de terme sans passer par la Fed), encours de
    dette quotidien, et solde du compte de trésorerie à la Fed (variable de liquidité de
    premier ordre : quand ce compte se remplit il retire des réserves du système bancaire).
  - `ingestion_eurostat.py` — activité réelle et enquêtes, zone euro + Allemagne, France,
    Italie, Espagne : production industrielle, ventes de détail, chômage, et **confiance
    industrielle comme substitut du PMI** (pendant européen des enquêtes Empire State /
    Philly Fed retenues côté US — les PMI S&P Global et l'ISM sont propriétaires).
  - `ingestion_bilans_nationaux.py` — bilans des banques centrales que FRED n'expose pas :
    Banque d'Angleterre, Reserve Bank of Australia (total, or et devises, titres locaux — la
    composition dit s'il s'agit de QE ou d'accumulation de réserves) et Banque du Canada
    (groupe complet, avec un index des libellés : l'API Valet nomme ses séries par des codes
    opaques que personne ne peut interpréter sans traduction).
  - `ingestion_cftc.py` — COT, positionnement spéculatif par contrat.
  - `ingestion_fomc_statements.py` / `ingestion_fomc_minutes.py` — texte brut Fed.
  - `ingestion_boe_declarations.py` — résumés de politique monétaire de la Banque
    d'Angleterre, repérés par motif de titre dans son flux d'actualités (qui mélange tous les
    sujets). **La BOJ manque encore** : ses déclarations sont publiées en PDF, ce qui
    demanderait une dépendance d'extraction PDF dans une CI partagée par tous les modèles.
  - `ingestion_bce_declarations.py` — déclarations de politique monétaire BCE. **Seule la
    déclaration préparée est extraite, pas la séance de questions-réponses** : deux registres
    linguistiques différents (texte écrit et négocié vs réponses orales spontanées), les
    mélanger fausserait toute mesure de ton ou de complexité comparée dans le temps.
  - `ingestion_souverains_g10.py` — courbes quotidiennes Canada (BoC Valet), Australie
    (table RBA F2), Suède (API Riksbank). Non retenus faute de source exploitable : NZ (RBNZ
    en HTTP 403 sur l'accès automatisé), Norvège (chemin des rendements non identifié),
    Suisse (cube SNB à dernière observation 2025-07, gel ou tri non chronologique — non
    tranché, donc non ingéré plutôt qu'ingéré à l'aveugle).
  - `ingestion_souverains_quotidiens.py` — courbes souveraines **quotidiennes** hors US :
    zone euro (BCE, AAA 2a/5a/10a + tous émetteurs 10a), Royaume-Uni (BoE 5a/10a/20a),
    Japon (MOF 2a/5a/10a/30a, historique depuis 1974).
  - `ingestion_bis_macro.py` — taux directeurs **quotidiens** des 12 blocs (le vrai taux fixé
    par la banque centrale, pas un proxy interbancaire mensuel) + ratio de service de la dette
    du secteur privé, 12 pays.

  Règle tenue depuis le premier jour : **aucune série n'entre sans avoir été testée en direct**,
  et chaque rejet reste documenté avec sa raison dans le fichier concerné (séries gelées,
  identifiants inexistants) pour ne pas être retenté à l'aveugle.
- **Modèles calculés à intervalle régulier**, orchestrés comme `run_all_modeles.py` dans GMDC —
  un échec isolé n'interrompt jamais les autres.
- **Centre de recherche horaire** (`rapports/`) : toutes les lectures sont regroupées par sujet
  économique, avec les CSV, les graphiques utiles, la fraîcheur, l'inventaire et le classeur.
  Il n'existe pas de publication parallèle propre à la Fed ni de copie technique des résultats.

## Combien -- ne pas le chercher ici

Les quantites (nombre de series par source, de modeles, de sorties) sont **generees** dans
`rapports/inventaire.md` a chaque execution, et ne sont pas recopiees dans ce fichier.

Raison, constatee par un audit le 2026-09-14 : les chiffres portes a la main dans MAP.md
avaient derive le jour meme de leur ecriture -- "67 series" quand il y en avait 73, "9 contrats"
quand il y en avait 32, et "96 modeles" coexistant avec "111 modeles" dans le meme document.
Un chiffre qui decrit le depot se compte, il ne s'ecrit pas.

## Structure

| Dossier | Rôle |
|---|---|
| `donnees/brut/` | Données importées, non retouchées |
| `recherche/modeles/` | Moteur de calcul des 8 familles ; aucun résultat à consulter ici |
| `rapports/donnees/` | Source unique des CSV calculés |
| `rapports/graphiques/` | Sélection de graphiques utiles, jamais un graphique par principe |
| `rapports/themes/` | Lectures regroupées par sujet économique |
| `rapports/` | Point d'entrée unique : lecture, qualité, inventaire et classeur |
| `automatisations/` | GitHub Actions + routines Claude |

## Où on en est

*(Cette section disait encore « squelette posé, rien construit encore » jusqu'au 2026-09-14 —
dérive de documentation corrigée ce jour, le repo tournait déjà depuis une semaine.)*

**État réel au 2026-09-14 :**

- Modèles répartis sur les 8 familles, tous testés sur données réelles, orchestrés par
  `run_all_modeles.py` (un échec isolé n'interrompt jamais les autres).
- **Workflows étagés** : ingestion lente à 06h00 UTC, marchés toutes les 30 minutes, COT
  hebdomadaire et publication complète toutes les heures, poussés par le bot
  `research-bot`. En exploitation normale, les données et états sont actualisés par ce bot ;
  les migrations de schéma restent des changements de code contrôlés et testés.
- **Couverture étendue le 2026-09-14** de 5 à 12 blocs de banques centrales, plus FX, matières
  premières, volatilité de taux et indices non-US (voir « Comment c'est automatisé »).

**Correctifs d'infra — faits le 2026-09-14 :**

1. ✅ **Timing du COT.** Le CFTC publie le vendredi vers 20h30 UTC ; l'ingestion tournait à
   06h00 UTC, donc la donnée du vendredi n'était ramassée que le lundi — ~2,5 jours de retard
   chaque semaine. Sorti dans `recherche-ingestion-cot.yml`, vendredi 21h30 UTC, avec un
   rattrapage le lundi matin si le vendredi échoue.
2. ✅ **Détection de péremption** — `controle_fraicheur.py`, lancé après chaque ingestion lente.
   Le seuil n'est pas configuré série par série mais **déduit du rythme de la série elle-même**
   (écart médian entre observations), parce que cinq seuils posés à la main se sont révélés
   faux le jour même de leur écriture. Calibré contre les six gels réellement observés sur ce
   dépôt. Sortie : `rapports/donnees/fraicheur.csv`.
3. ✅ **Alerte.** Une série classée GELÉE fait échouer le workflow — c'est le signal. Une série
   seulement SUSPECTE est signalée sans faire échouer : une alerte qui crie tous les jours est
   désactivée en une semaine et ne protège plus rien.
4. ✅ **Cadence étagée** en trois workflows : lent (macro et textes, 1×/jour ouvré), marchés
   (FX, matières premières, vol, indices — toutes les 30 min de 07h à 21h UTC), COT
   (hebdomadaire).
5. ✅ **Hygiène CI** : cache pip sur les trois workflows, et un groupe de concurrence commun
   (`recherche-push`) qui sérialise tout ce qui pousse sur `main` — sans lui, deux exécutions
   simultanées se marchent dessus entre le rebase et le push.
6. ✅ **Les modèles lisent les données** — 12 modèles ajoutés le 2026-09-14, un par famille de
   données ingérées ce jour, tous verts en CI.
7. ✅ **Détection des ruptures de périmètre** — `controle_ruptures.py`. Quand l'univers change
   (un contrat ajouté, un historique rallongé), les lignes accumulées avant et après ne sont
   plus comparables et rien ne le signalait. Deux ruptures réelles trouvées à l'audit du
   2026-09-14 : `crowding_cross_asset` passant de « 3 tendus sur 15 » à « 15 sur 32 » d'une
   semaine à l'autre, et `nombre_effectif_paris` de 8,54 à 13,39 — dans les deux cas
   l'élargissement du COT, pas le marché. Le contrôle distingue un **dénominateur** (rupture)
   d'un **résultat** (variation normale), sans quoi il crierait à chaque mesure.
8. ✅ **Chaque modèle a une sortie.** Le CSV est la sortie canonique ; les vues suivantes
   rendent le dispositif lisible sans dupliquer les fichiers :
   - `rapports/lecture-du-jour.md` — la première page. L'orchestrateur capture la phrase
     interprétable de chaque modèle et les regroupe par sujet économique. Sans elle, ces lectures
     n'existaient que dans le journal d'exécution et disparaissaient après le run : le dépôt
     calculait beaucoup et ne disait rien. Les 12 modèles qui **énumèrent sans conclure** y
     sont marqués _(sans synthèse)_ plutôt que masqués.
   - `rapports/etat-recherche.xlsx` — un classeur, une feuille par fichier d'état, valeurs
     écrites comme des nombres et non du texte.
   - `rapports/graphiques/` — une sélection explicite. Une figure n'est créée que si elle
     accélère la lecture d'une évolution temporelle ou d'une comparaison ; les tableaux,
     contrôles et sorties textuelles restent volontairement en CSV seul.
9. ✅ **Scheduler réactivé le 2026-09-25.** Les workflows étaient encore marqués `active`, mais
   le dépôt lui-même avait été archivé : GitHub le plaçait en lecture seule et ne lançait plus
   aucun cron depuis le 2026-09-22. Le dépôt a été désarchivé ; la cause n'était ni le YAML, ni
   les permissions Actions, ni les scripts d'ingestion.

**Décision actée le 2026-09-14 — les modèles qui énumèrent sans conclure restent tels quels.**
Douze modèles produisent une ligne par pays, par contrat ou par paire, sans phrase de synthèse.
Ils sont signalés _(sans synthèse)_ dans la lecture du jour. Décision de 001 : ne pas leur en
écrire une automatiquement — leur sortie est de la matière première, et l'interprétation se
fait au moment où l'on rédige la note du jour ou une thèse. Une synthèse générée d'avance
n'ajouterait rien et figerait une lecture qui dépend du contexte.

**Trous connus, documentés et non résolus :**

- ~~Inflation hors US~~ — **résolu le 2026-09-14** via `ingestion_bis_cpi.py` (BIS, 12 blocs,
  frais à 2026-07). Restriction : indice de prix seulement, pas d'inflation sous-jacente
  (core) ni de décomposition par poste.
- **Chômage suisse** : aucune série exploitable trouvée sur FRED.
- ~~Souverains non-US en quotidien~~ — **résolu le 2026-09-14** (BCE, BoE, MOF Japon).
- **PMI, ventes de détail, production industrielle** : couverts pour les **US** (FRED) et
  pour la **zone euro + DE/FR/IT/ES** (Eurostat) depuis le 2026-09-14. **Restent absents :
  Royaume-Uni, Japon, Chine, Corée** — chacun demanderait sa source nationale (ONS, e-Stat,
  NBS, KOSIS), non ouvert à ce stade.
- **Réserves de change hors US** : le FMI (via DBnomics) les publie en **mensuel**, ce qui est
  la bonne fréquence, mais le miroir accuse ~14 mois de retard (Chine à 2025-07 au
  2026-09-14). Utilisable pour de l'étude historique, pas pour détecter une intervention.
  Les sources nationales (SNB, BOJ, SAFE) seraient nécessaires pour du courant — non ouvert.
- ~~Calendrier d'émission souveraine~~ — **résolu le 2026-09-14** (Trésor US, FiscalData),
  ainsi que le déficit budgétaire **mensuel** et le compte courant côté FRED.
- **Réserves de change hors US** : uniquement en **annuel** (Banque mondiale) — testé, mais
  une fréquence annuelle ne permet pas de détecter une intervention de change, donc non
  ingéré plutôt que de donner une fausse impression de couverture.
- **Flux de fonds** : pas de source gratuite. Les données de référence (EPFR, Lipper) sont
  propriétaires. Non résolu.
- **Volatilité zone euro (VSTOXX)** : indisponible via l'endpoint utilisé.
- **NLP** : la BCE et la Banque d'Angleterre sont désormais lues par
  `modele_ton_banques_centrales`, qui applique le même lexique aux trois institutions. Les
  autres modèles NLP restent écrits contre le FOMC seul — ce n'est pas un oubli : un modèle de
  désaccord au vote ou d'écart communiqué/minutes n'a pas d'équivalent direct chez les deux
  autres, qui ne publient ni les mêmes documents ni la même procédure. **La BOJ reste absente**
  (déclarations en PDF).
