# MAP — repère du dispositif

Ce fichier est le seul point d'orientation de ce dépôt (même convention que
`global-macro-desk-cloud` — commence toujours ici, humain ou Claude Code).

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

Même schéma que GMDC (ingestion → modèles → état → visualisations → rapports) :

- **Ingestion programmée** (`donnees/brut/`), 1×/jour ouvré :
  - `ingestion_fred.py` — 45 séries officielles. 12 blocs de banques centrales (G10 complet +
    Chine + Corée) en taux directeur et emploi, courbe des taux US (3M/2a/5a/10a/30a),
    rendements réels TIPS + point mort d'inflation, souverains 10 ans non-US, spreads crédit
    IG/HY US et corporate émergent, cycle immobilier, balance commerciale, dette publique.
  - `ingestion_marches.py` — 25 marchés : FX G10 + DXY + CNY/KRW, 5 matières premières
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
  - `ingestion_cftc.py` — COT, 9 contrats.
  - `ingestion_fomc_statements.py` / `ingestion_fomc_minutes.py` — texte brut Fed.
  - `ingestion_bce_declarations.py` — déclarations de politique monétaire BCE. **Seule la
    déclaration préparée est extraite, pas la séance de questions-réponses** : deux registres
    linguistiques différents (texte écrit et négocié vs réponses orales spontanées), les
    mélanger fausserait toute mesure de ton ou de complexité comparée dans le temps.
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
- **Rapports automatiques** (`rapports/`) : pulse quotidien, revue hebdomadaire, dashboard de
  régimes — à construire une fois qu'il y a quelque chose à résumer.

## Structure

| Dossier | Rôle |
|---|---|
| `donnees/brut/` | Données importées, non retouchées |
| `recherche/modeles/` | Code des 8 familles, une lane chacune |
| `recherche/etat/` | Résultat calculé — la donnée, jamais le code |
| `recherche/visualisations/` | Un graphique par modèle |
| `rapports/` | Synthèses automatiques |
| `automatisations/` | GitHub Actions + routines Claude |

## Où on en est

*(Cette section disait encore « squelette posé, rien construit encore » jusqu'au 2026-09-14 —
dérive de documentation corrigée ce jour, le repo tournait déjà depuis une semaine.)*

**État réel au 2026-09-14 :**

- **96 modèles** répartis sur les 8 familles, tous testés sur données réelles, orchestrés par
  `run_all_modeles.py` (un échec isolé n'interrompt jamais les autres).
- **Deux workflows** : ingestion à 06h00 UTC, modèles à 06h30 UTC, jours ouvrés, poussés par
  le bot `research-bot`. Les fichiers `donnees/brut/` et `recherche/etat/` ne sont **jamais**
  committés depuis une session de travail — seulement par ce bot.
- **Couverture étendue le 2026-09-14** de 5 à 12 blocs de banques centrales, plus FX, matières
  premières, volatilité de taux et indices non-US (voir « Comment c'est automatisé »).

**Chantiers annexes — correctifs d'infra à enchaîner une fois les ingestions terminées
(identifiés le 2026-09-14, aucun n'est encore fait) :**

1. **Timing du COT — bug réel.** Le CFTC publie le vendredi vers 20h30 UTC ; l'ingestion tourne
   à 06h00 UTC. La donnée de positionnement du vendredi n'est donc ramassée que le lundi
   matin, ~2,5 jours de retard chaque semaine. À sortir sur son propre créneau.
2. **Aucune détection de péremption côté FRED.** `ingestion_marches.py` et
   `ingestion_yfinance_indices.py` ont un garde-fou `MAX_JOURS_RETARD` ; `ingestion_fred.py`
   n'en a aucun. Or on sait que des séries FRED gèlent (3 rencontrées le 2026-09-14). Une
   série qui se fige passerait inaperçue et les modèles continueraient à calculer dessus.
3. **Aucune alerte.** Ni opérationnelle (workflow en échec, série morte, modèle planté), ni de
   recherche (indicateur à un extrême historique). `if: always()` masque d'autant plus les
   échecs partiels. Contrainte de périmètre à respecter : une alerte reste **descriptive**,
   jamais un signal de décision — sinon on sort du mandat de ce repo.
4. **Cadence à étager.** Le macro lent (FRED, textes FOMC) reste à 1×/jour — c'est correct et
   accélérer ne produirait que des fichiers identiques. Mais le FX, les matières premières,
   la vol et les indices ajoutés le 2026-09-14 bougent en continu : ils justifient leur propre
   créneau intrajournalier, séparé du lent.
5. **Hygiène CI** : pas de cache pip (réinstallation complète à chaque run), pas de garde de
   concurrence alors que les deux workflows poussent sur `main`.
6. **Les 96 modèles ne consomment pas encore les nouvelles données** — ils ont été écrits
   contre l'ancien jeu. Ingérer n'est pas consommer.

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
- **NLP** : l'ingestion BCE existe depuis le 2026-09-14, mais **aucun modèle ne la lit
  encore** — les 12 modèles NLP restent écrits contre le FOMC. C'est un cas particulier du
  chantier 6 ci-dessus (ingérer n'est pas consommer).
