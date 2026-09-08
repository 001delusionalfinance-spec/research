# donnees/brut/

Données importées, jamais retouchées à la main — un script d'ingestion écrit ici, les modèles
lisent d'ici, jamais l'inverse. Voir `MAP.md` (racine) pour la vision d'ensemble.

Deux sources actives : FRED (`fred/`, `ingestion_fred.py`, 10 séries — taux directeurs et
chômage, 5 blocs) et CFTC (`cftc/`, `ingestion_cftc.py`, 9 marchés — positionnement
spéculatif hebdomadaire). yfinance à ajouter selon le besoin réel, pas préventivement.
