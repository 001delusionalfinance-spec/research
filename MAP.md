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

- **Ingestion programmée** (`donnees/brut/`) : FRED multi-pays, yfinance (FX/taux/matières
  premières/indices), CFTC (COT) — à étendre selon les besoins réels, pas préventivement.
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

Squelette posé le 2026-09-08, rien construit encore. Prochaine étape à décider avec 001 : quel
module récupérer en premier depuis le `git log` de GMDC (les modèles de recherche pure qui y
avaient été construits — event-study/NLP, factoriel, jump-tail, ML walk-forward, etc. —
récupérables indépendamment du framework de thèse/trade, qui lui reste dans GMDC), ou quelle
ingestion démarrer en premier côté données macro pures.
