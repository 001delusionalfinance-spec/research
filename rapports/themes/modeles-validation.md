# Modeles predictifs et validation

Relations statistiques, previsions, tests hors echantillon et robustesse des modeles.

Mis a jour : **2026-09-25 14:10 UTC** · 17 lectures.

[Retour au tableau de bord](../README.md)

### Causalite granger

causalite Granger detectee : SP500_cause_VIX (lag=5)

_Statut **OK** · observation 2026-09-24 · moteur `statistique` · [donnees](../donnees/causalite_granger.csv)_


### Dependance queue

518/7545 jours conjointement extremes (SP500 pire 10% ET VIX pire 10%), P observee=0.0687 vs P sous independance=0.0100 -- coefficient de dependance de queue=6.87 (dependance reelle)

_Statut **OK** · observation 2026-09-24 · moteur `statistique` · [donnees](../donnees/dependance_queue.csv)_


### Walkforward direction

7515 predictions walk-forward -- momentum 5j=0.4961 vs baseline majoritaire=0.5376 -- NE BAT PAS la baseline (resultat honnete, pas ajuste pour paraitre mieux)

_Statut **OK** · observation 2026-09-24 · moteur `ml` · [donnees](../donnees/walkforward_direction_sp500.csv)_


### Anomalie multivariee

distance de Mahalanobis=0.421 (seuil 3.0) -- jour ordinaire

_Statut **OK** · observation 2026-09-24 · moteur `ml` · [donnees](../donnees/anomalie_multivariee.csv)_


### Test overfitting

meilleure fenetre in-sample=23j (accuracy=0.5166) vs meme fenetre en walk-forward=0.5164 -- ecart=+0.0002 (ecart faible)

_Statut **OK** · observation 2026-09-24 · moteur `ml` · [donnees](../donnees/test_overfitting_momentum.csv)_


### Prevision vol regression

regression AR(1) (a=0.000116, b=0.2096) MSE=2.9848e-07 vs baseline persistance MSE=3.8342e-07 -- BAT la baseline (resultat honnete, pas ajuste)

_Statut **OK** · observation 2026-09-24 · moteur `ml` · [donnees](../donnees/prevision_vol_regression.csv)_


### Kmeans regimes

2048 points, k=3 -- point actuel (VIX=15.2, spread=+0.26, taux=3.88%) -> cluster 1 (tailles : {0: 357, 1: 1367, 2: 324}) -- regime calme (VIX du cluster en-dessous de la moyenne historique)

_Statut **OK** · observation 2026-09-23 · moteur `ml` · [donnees](../donnees/kmeans_regimes.csv)_


### Ensemble signaux

7515 predictions -- momentum=0.4961, vix=0.4990, ensemble=0.4990, baseline=0.5376 -- ensemble NE BAT PAS la baseline

_Statut **OK** · observation 2026-09-24 · moteur `ml` · [donnees](../donnees/ensemble_signaux.csv)_


### Screening features

2/4 features avec un lien univarie significatif (p<0.05, sans correction multiple-testing ici -- seulement 4 tests)  _(sans synthese)_

_Statut **OK** · observation 2026-09-24 · moteur `ml` · [donnees](../donnees/screening_features.csv)_


### Couts transaction

7515 predictions, 1512 changements de position (5pb/changement) -- rendement cumule brut=-93.11%, cout total=53.05%, net=-96.77% -- les frais mangent une part importante du rendement (>50% du brut)

_Statut **OK** · observation 2026-09-24 · moteur `ml` · [donnees](../donnees/couts_transaction.csv)_


### Regression multifeatures

coefs (intercept=0.00029, momentum5j=-0.0326, var_vix=0.00027) -- R2 out-of-sample=0.0102 (modele bat la moyenne)

_Statut **OK** · observation 2026-09-24 · moteur `ml` · [donnees](../donnees/regression_multifeatures.csv)_


### Decomposition variance

R² SP500~DGS10 (60j) = 0.2435 -- 24.3% de la variance des rendements SP500 expliquee par les variations du taux 10 ans (le reste = idiosyncratique/autres facteurs)

_Statut **OK** · observation 2026-09-23 · moteur `statistique` · [donnees](../donnees/decomposition_variance.csv)_


### Test chow

test de Chow (taux 10 ans, 1ere vs 2eme moitie des 12 derniers mois) : F=573.127, p=0.0000 -- RUPTURE structurelle significative

_Statut **OK** · observation 2026-09-23 · moteur `statistique` · [donnees](../donnees/test_chow.csv)_


### Arima

ARIMA(1,1,1) sur 100 previsions 1-jour test : RMSE=2.332 vs baseline naive MSE=5.464 -- ARIMA bat la persistance simple

_Statut **OK** · observation 2026-09-25 · moteur `series-temporelles` · [donnees](../donnees/arima.csv)_


### Stacking

poids appris (momentum=-0.081, baseline=0.090, biais=0.090) -- accuracy stacking=0.5468 vs momentum seul=0.5029, baseline seule=0.5468 sur 2255 points test -- stacking NE BAT PAS la baseline, meilleur=stacking / baseline (ex-aequo)

_Statut **OK** · observation 2026-09-24 · moteur `ml` · [donnees](../donnees/stacking.csv)_


### Decision stump

seuil appris=-1.530 (sens=False) -- accuracy stump=0.5459 vs baseline=0.5477 sur 2264 points test -- stump NE BAT PAS la baseline

_Statut **OK** · observation 2026-09-24 · moteur `ml` · [donnees](../donnees/decision_stump.csv)_


### Importance permutation

R2 base=0.0102 -- importance momentum5j=0.00586, importance variation_vix=0.01331 -- VIX plus important

_Statut **OK** · observation 2026-09-24 · moteur `ml` · [donnees](../donnees/importance_permutation.csv)_

