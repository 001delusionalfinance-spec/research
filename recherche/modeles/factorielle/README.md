# factorielle/

Exposition value/momentum/carry/quality, cross-asset (pas limité aux actions détenues comme
dans GMDC — ici l'univers est libre). Voir `MAP.md` (racine).

## `modele_momentum_prix.py` (2026-09-08)

Momentum de prix S&P 500, définition académique 12-1 mois (Jegadeesh-Titman 1993 : rendement
12 mois en excluant le dernier mois, le retournement court terme post-forte-hausse étant un
effet distinct documenté séparément).

**Limite honnête** : c'est du *time-series momentum* (un seul actif dans le temps), pas encore
une vraie analyse factorielle cross-sectional (comparer plusieurs actifs entre eux). Première
brique en attendant que l'univers d'instruments s'élargisse au-delà de SP500/VIX — les deux
approches sont réelles et documentées séparément dans la littérature (time-series momentum :
Moskowitz/Ooi/Pedersen 2012), pas un raccourci dégradé.

`ingestion_yfinance_indices.py` étendu de 1 à 2 ans d'historique pour laisser de la marge au
calcul 12 mois (testé : un an pile aurait fait échouer le calcul dès que la donnée la plus
ancienne s'approche de la limite).

Testé avec de vraies données : momentum 12-1 mois = +19,44% (SP500 12m = +18,39%, cohérent).

## `modele_carry_proxy.py` (2026-09-08)

Différentiel de taux directeur entre chaque bloc et les US — proxy du carry trade classique
(avant effet de change, limite assumée : pas de prix spot FX ingéré pour l'instant). Testé
réel : Japon -2,79pt vs US (carry le plus négatif), UK +0,10pt (seul positif).

## `modele_beta_vol.py` (2026-09-08)

Beta glissant (60j) du S&P 500 au VIX — pas juste la corrélation (déjà dans `statistique/`)
mais l'AMPLITUDE de la réaction. Testé réel : -0,00521 (SP500 perd ~0,52% pour +1pt de VIX).
