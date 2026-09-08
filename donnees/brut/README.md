# donnees/brut/

Données importées, jamais retouchées à la main — un script d'ingestion écrit ici, les modèles
lisent d'ici, jamais l'inverse. Voir `MAP.md` (racine) pour la vision d'ensemble.

Rien ingéré pour l'instant. Sources prévues, à démarrer une par une selon le besoin réel (pas
préventivement) : FRED (séries macro multi-pays), yfinance (FX, taux, matières premières,
indices), CFTC (positionnement COT).

Convention reprise de `global-macro-desk-cloud` : un sous-dossier par source
(`fred/`, `yfinance/`, `cftc/`), un fichier par série/instrument.
