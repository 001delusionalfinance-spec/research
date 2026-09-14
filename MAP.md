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
  - `ingestion_cftc.py` — COT, 9 contrats.
  - `ingestion_fomc_statements.py` / `ingestion_fomc_minutes.py` — texte brut Fed.

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

**Trous connus, documentés et non résolus :**

- **Inflation hors US** : les séries CPI internationales gratuites sur FRED (source OCDE) ont
  12 à 60+ mois de retard — testées et rejetées une par une. Il faudra taper Eurostat / ONS /
  e-Stat / NBS en direct. C'est le trou le plus gênant : sans CPI non-US, pas de comparaison
  d'inflation entre blocs.
- **Chômage suisse** : aucune série exploitable trouvée sur FRED.
- **Souverains non-US en fréquence quotidienne** : seulement du mensuel (source OCDE).
- **PMI, ventes de détail, production industrielle** : absents pour tous les pays.
- **Réserves de change, flux de fonds, calendrier d'émission souveraine** : absents.
- **Volatilité zone euro (VSTOXX)** : indisponible via l'endpoint utilisé.
- **NLP** : encore 100 % Fed (12 modèles sur les communiqués et minutes du FOMC), aucune autre
  banque centrale — alors que le patron de code est réutilisable tel quel pour la BCE.
