# factorielle/

Exposition value/momentum/carry/quality, cross-asset (pas limité aux actions détenues comme
dans GMDC — ici l'univers est libre). Voir `MAP.md` (racine).

## `modele_momentum_prix.py` (2026-09-08)

Momentum de prix S&P 500, définition académique 12-1 mois (Jegadeesh-Titman 1993 : rendement
12 mois en excluant le dernier mois, le retournement court terme post-forte-hausse étant un
effet distinct documenté séparément).

**Limite honnête** : c'est du *time-series momentum* (un seul actif dans le temps), pas encore
une vraie analyse factorielle cross-sectional (comparer plusieurs actifs entre eux). Les deux
approches sont réelles et documentées séparément dans la littérature (time-series momentum :
Moskowitz/Ooi/Pedersen 2012), pas un raccourci dégradé. Depuis l'ajout des 10 ETF sectoriels
(`modele_rotation_sectorielle.py` ci-dessous), une vraie comparaison cross-sectional devient
possible — pas encore construite comme telle, la brique de données l'est.

`ingestion_yfinance_indices.py` étendu de 1 à 2 ans d'historique (2026-09-08 matin) puis à
30 ans pour SP500/VIX (2026-09-08 après-midi, pour `modele_stress_test_historique.py` en
`risque/`) — laisse largement la marge nécessaire au calcul 12 mois.

Testé avec de vraies données : momentum 12-1 mois = +19,44% (SP500 12m = +18,41%, cohérent).

## `modele_carry_proxy.py` (2026-09-08)

Différentiel de taux directeur entre chaque bloc et les US — proxy du carry trade classique
(avant effet de change, limite assumée : pas de prix spot FX ingéré pour l'instant). Testé
réel : Japon -2,79pt vs US (carry le plus négatif), UK +0,10pt (seul positif).

## `modele_beta_vol.py` (2026-09-08)

Beta glissant (60j) du S&P 500 au VIX — pas juste la corrélation (déjà dans `statistique/`)
mais l'AMPLITUDE de la réaction. Testé réel : -0,00521 (SP500 perd ~0,52% pour +1pt de VIX).

## `modele_rotation_sectorielle.py` (2026-09-08)

Momentum 3 mois des 10 secteurs S&P 500 (ETF SPDR), classement leaders/retardataires — lecture
objective, pas d'interprétation automatique de phase de cycle (ce dépôt ne décide rien). Testé
réel : Énergie en tête (+12,62%), Immobilier dernier (-1,92%).

## `modele_saisonnalite.py` (2026-09-08)

Facteur saisonnier "Sell in May" testé statistiquement (test t, scipy), pas affirmé — écrit
avec seulement 2 ans d'historique (limite documentée à l'époque), profite désormais des 30 ans
disponibles pour SP500. Testé réel : différence été/hiver non significative (p=0,32).

## `modele_dispersion_sectorielle.py` (2026-09-08)

Écart-type des rendements 3 mois entre les 10 secteurs — dispersion élevée = environnement
favorable au stock/sector-picking. Testé réel : dispersion=5,02pt, étendue=14,77pt.

## `modele_low_volatility.py` (2026-09-08)

Test de l'anomalie low-vol (Ang et al. 2006) sur les 10 secteurs — testé, pas affirmé, limite de
puissance statistique documentée (n petit). Testé réel : anomalie NON confirmée sur cet
échantillon (Sharpe bas-vol=0,55 < Sharpe haut-vol=0,75).

## `modele_facteur_qualite_credit.py` (2026-09-08)

Écart HY-IG (`BAMLH0A0HYM2`/`BAMLC0A0CM`, ajoutés à `ingestion_fred.py`) — prime de risque
crédit implicite, indépendante des mesures de positionnement/prix actions. Testé réel :
écart=1,87pt, variation 6m=-20,1% (spread qui se resserre).

## `modele_momentum_cross_sectional.py` (2026-09-08)

Le VRAI facteur momentum académique (Jegadeesh-Titman) : spread de rendement entre le tercile
gagnant et le tercile perdant des 10 secteurs, au même instant — complète
`modele_rotation_sectorielle.py` (classement) en construisant le facteur lui-même. Testé réel :
spread=+11,85pt (Énergie/Finance/Santé vs Services collectifs/Consommation discrétionnaire/
Immobilier).

## `modele_qualite_regime_macro.py` (2026-09-08)

Facteur "qualité" appliqué au régime macro (stabilité du taux directeur + VIX, pas un
fondamental d'entreprise faute de données) — distinct du niveau (déjà mesuré par
`modele_conditions_financieres.py`). Testé réel : score=-0,0338 (instabilité VIX dominante).
