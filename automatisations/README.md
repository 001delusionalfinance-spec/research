# automatisations/

L'automatisation du dépôt tourne sur GitHub Actions (`.github/workflows/`), sans intervention quotidienne.

| Workflow | Rôle | Déclenchement |
|---|---|---|
| `recherche-modeles.yml` | Mise à jour complète : ingestion, calcul des modèles, publication des rapports | Toutes les heures (deux départs par heure) et à la demande |
| `recherche-surveillance.yml` | Surveillance du cycle horaire | Toutes les cinq minutes |
| `recherche-ingestion.yml` | Relance manuelle des sources macro | À la demande |
| `recherche-ingestion-marches.yml` | Relance manuelle des marchés | À la demande |
| `recherche-ingestion-cot.yml` | Relance manuelle du positionnement CFTC | À la demande |
| `tests.yml` | Compilation et tests automatiques | À chaque envoi sur `main`, à chaque pull request et à la demande |

Le détail de la chaîne (ingestion, modèles, publication) est dans [`MAP.md`](../MAP.md), section « Comment c'est automatisé ».
