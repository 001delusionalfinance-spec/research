# Research

**Un pipeline de recherche macroéconomique automatisé : données publiques officielles, une centaine de modèles, un rapport lisible mis à jour plusieurs fois par jour.**

*English: an automated macro research pipeline. It pulls official public data (central banks, statistics offices, CFTC), runs about a hundred models across eight method families, and publishes a plain-language report that refreshes several times a day. Research only: no trade signals, no investment advice.*

## Lire en deux minutes

1. **[Le rapport du jour](rapports/lecture-du-jour.md)** : l'état du monde macro en une page, par sujet (banques centrales, cycle, taux et liquidité, marchés, positionnement, risques).
2. **[Le centre de recherche](rapports/README.md)** : les sept rapports thématiques, les données et les graphiques.
3. **[Qualité et fraîcheur des sources](rapports/qualite.md)** : ce qui est à jour, ce qui ne l'est pas, et pourquoi.
4. **[Le classeur complet](rapports/etat-recherche.xlsx)** : toutes les sorties dans un seul fichier Excel.

## Ce que le dépôt fait

| Étape | Contenu |
|---|---|
| **Ingestion** | Séries officielles téléchargées sans retouche : FRED, BIS, BCE, Banque d'Angleterre, Eurostat, Trésor américain, CFTC (positionnement), communiqués et minutes du FOMC, marchés (change, matières premières, indices). |
| **Modèles** | Huit familles : macro, statistique, séries temporelles, factorielle, risque, positionnement et comportement, analyse de texte (discours de banques centrales), apprentissage automatique avec validation *walk-forward*. |
| **Publication** | Chaque modèle produit une lecture en une phrase, avec sa date d'observation, ses données (CSV) et, quand un graphique aide vraiment, un graphique. |
| **Contrôle** | Fraîcheur des sources, détection de ruptures, cohérence des résultats et tests automatiques. |

Douze banques centrales sont suivies (G10, Chine, Corée du Sud) : taux directeurs, bilans, ton des communiqués, chemin de taux attendu, règle de Taylor.

## Principes

- **Une lecture, jamais une décision.** Chaque modèle décrit un mécanisme : il n'émet ni signal de trade ni recommandation.
- **Aucune série n'entre sans avoir été testée en direct.** Chaque rejet (série gelée, source bloquée, identifiant inexistant) est documenté avec sa raison.
- **Un modèle qui ne bat pas sa référence se documente, il ne se cache pas.**
- **Les chiffres du dépôt se comptent, ils ne s'écrivent pas** : les quantités exactes sont générées dans [`rapports/inventaire.md`](rapports/inventaire.md) à chaque exécution.

## Fonctionnement

Le dépôt tourne seul sur GitHub Actions (planification, ingestion, calcul des modèles, publication). Un compte automatique (`research-bot`) enregistre chaque mise à jour, ce qui explique l'historique de commits « Recherche - mise à jour complète ». La surveillance vérifie le cycle toutes les cinq minutes et six fichiers de tests couvrent la publication, la fraîcheur, les écritures de données et les modèles de la Fed.

## Structure

| Dossier | Rôle |
|---|---|
| [`rapports/`](rapports/README.md) | Point d'entrée : lectures, données, graphiques, qualité, inventaire, classeur |
| `recherche/modeles/` | Scripts d'ingestion et modèles des huit familles |
| `donnees/brut/` | Données importées, non retouchées |
| `tests/` | Tests automatiques |
| `.github/workflows/` | Planification et chaîne d'exécution |
| [`MAP.md`](MAP.md) | Architecture détaillée, pour les mainteneurs |

## Limites

- Recherche personnelle et pédagogique : aucun conseil en investissement.
- Les rapports sont générés automatiquement, sans accents, et certaines lectures sont signalées « sans synthèse » lorsqu'un modèle énumère des résultats sans conclusion globale.
- Les graphiques sont volontairement sobres : ils ne sont ajoutés que s'ils rendent une comparaison plus lisible.
- La Banque du Japon manque encore côté texte (ses déclarations sont publiées en PDF).

## Auteur

**Nadime ATIA**, étudiant en licence AEF au CNAM, basé à Rennes. Le projet est conçu, spécifié et relu par l'auteur ; le code est écrit avec des assistants IA, sous tests et vérification des résultats.

[LinkedIn](https://www.linkedin.com/in/nadime-atia-830503406/) · [pro@rebirth-core.com](mailto:pro@rebirth-core.com)
