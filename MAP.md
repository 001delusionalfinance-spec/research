# MAP — repère du dispositif

Ce fichier est le seul point d'orientation de ce dépôt (même convention que
`global-macro-desk-cloud` — commence toujours ici, humain ou Claude Code).

## Ce que c'est, ce que ce n'est pas

Hub de recherche macroéconomique **complètement séparé** du fonds souverain
(`global-macro-desk-cloud`, mécanique, zéro décision liée à ici). Ici, l'objectif est
d'**apprendre en s'entraînant en paper trading** — pas de gérer un capital réel, pas de
comptabilité institutionnelle, pas de registre juridique. Un vrai atelier de recherche, pas un
desk. `theses-macro/` et `strategies-rules/` avaient été supprimés de GMDC le 2026-09-06
précisément pour vivre ici.

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

## Comment c'est recherché (le "comment") — 10 familles, même taxonomie que le Q1/Q2 déjà
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
9. **Thèse** — le cœur discrétionnaire : une thèse macro (framework à récupérer depuis
   `git log` de GMDC — `theses-macro/mandate-and-protocol.md`, `template-these.md`, journal
   bayésien) part d'un fait vérifié, articule un mécanisme, se falsifie explicitement.
   (`theses/`)
10. **Paper trading** — une thèse validée devient une construction de trade (instrument,
    sizing, invalidation), exécutée sur un compte IBKR paper, suivie jusqu'à clôture.
    (`paper-trading/`)

## Comment c'est automatisé

Même schéma que GMDC (ingestion → modèles → état → visualisations → rapports), en plus large :

- **Ingestion programmée** (`donnees/brut/`) : FRED multi-pays, yfinance (FX/taux/matières
  premières/indices), CFTC (COT) — à étendre selon les besoins réels, pas préventivement.
- **Modèles calculés à intervalle régulier**, orchestrés comme `run_all_modeles.py` dans GMDC —
  un échec isolé n'interrompt jamais les autres.
- **Détection → proposition de thèse** : un régime qui bascule ou une corrélation qui casse peut
  déclencher une proposition de sujet, jamais une thèse écrite automatiquement sans validation
  humaine.
- **Cycle de vie d'une thèse** : proposition → construction de trade → exécution paper → suivi
  continu (journal bayésien, pas d'attente de la clôture pour écrire) → clôture → post-mortem
  honnête (le vrai "pourquoi" quand ça rate, pas "pas de chance").
- **Rapports automatiques** (`rapports/`) : pulse quotidien, revue hebdomadaire, dashboard de
  régimes — à construire une fois qu'il y a quelque chose à résumer.

## Structure

| Dossier | Rôle |
|---|---|
| `donnees/brut/` | Données importées, non retouchées |
| `recherche/modeles/` | Code des 8 premières familles (macro → ML), une lane par famille |
| `recherche/etat/` | Résultat calculé — la donnée, jamais le code |
| `recherche/visualisations/` | Un graphique par modèle |
| `theses/` | Framework de thèse macro discrétionnaire (à récupérer depuis GMDC) |
| `paper-trading/` | Constructions de trade, blotter paper, suivi de performance |
| `rapports/` | Synthèses automatiques |
| `automatisations/` | GitHub Actions + routines Claude |

## Où on en est

Squelette posé le 2026-09-08, rien construit encore. Prochaine étape à décider avec 001 : quel
module récupérer en premier depuis le `git log` de GMDC (event-study/NLP earnings, valuation
DCF/comparables, Bayesian updating, factoriel single-name, jump-tail... tout ce qui a été
supprimé le 2026-09-06 par recentrage sur le fonds souverain), ou quelle ingestion démarrer en
premier côté données macro pures.

Délibérément pas de `GOUVERNANCE.md`/registre juridique façon GMDC ici — ce n'est pas un mandat
partagé avec un tiers sur du capital réel, juste un atelier d'apprentissage. À reconsidérer si
ça devient nécessaire, pas par défaut.
