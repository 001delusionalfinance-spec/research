# Modeles predictifs et validation

Relations statistiques, previsions, tests hors echantillon et robustesse des modeles.

Mis a jour : **2026-09-30 12:46 UTC** · 17 lectures.

[Retour au tableau de bord](../README.md)

### Causalite granger

causalite Granger detectee : SP500_cause_VIX (lag=5)

_Statut **OK** · observation 2026-09-29 · moteur `statistique` · [donnees](../donnees/causalite_granger.csv)_


### Dependance queue

518/7546 jours conjointement extremes (SP500 pire 10% ET VIX pire 10%), P observee=0.0686 vs P sous independance=0.0100 -- coefficient de dependance de queue=6.86 (dependance reelle)

_Statut **OK** · observation 2026-09-29 · moteur `statistique` · [donnees](../donnees/dependance_queue.csv)_


### Walkforward direction

7516 predictions walk-forward -- momentum 5j=0.4959 vs baseline majoritaire=0.5373 -- NE BAT PAS la baseline (resultat honnete, pas ajuste pour paraitre mieux)

_Statut **OK** · observation 2026-09-29 · moteur `ml` · [donnees](../donnees/walkforward_direction_sp500.csv)_


### Anomalie multivariee

distance de Mahalanobis=0.512 (seuil 3.0) -- jour ordinaire

_Statut **OK** · observation 2026-09-29 · moteur `ml` · [donnees](../donnees/anomalie_multivariee.csv)_


### Test overfitting

meilleure fenetre in-sample=23j (accuracy=0.5163) vs meme fenetre en walk-forward=0.5160 -- ecart=+0.0003 (ecart faible)

_Statut **OK** · observation 2026-09-29 · moteur `ml` · [donnees](../donnees/test_overfitting_momentum.csv)_


### Prevision vol regression

regression AR(1) (a=0.000116, b=0.2096) MSE=2.9848e-07 vs baseline persistance MSE=3.8344e-07 -- BAT la baseline (resultat honnete, pas ajuste)

_Statut **OK** · observation 2026-09-29 · moteur `ml` · [donnees](../donnees/prevision_vol_regression.csv)_


### Kmeans regimes

2048 points, k=3 -- point actuel (VIX=16.1, spread=+0.32, taux=3.88%) -> cluster 1 (tailles : {0: 357, 1: 1367, 2: 324}) -- regime calme (VIX du cluster en-dessous de la moyenne historique)

_Statut **OK** · observation 2026-09-28 · moteur `ml` · [donnees](../donnees/kmeans_regimes.csv)_


### Ensemble signaux

7516 predictions -- momentum=0.4959, vix=0.4988, ensemble=0.4988, baseline=0.5373 -- ensemble NE BAT PAS la baseline

_Statut **OK** · observation 2026-09-29 · moteur `ml` · [donnees](../donnees/ensemble_signaux.csv)_


### Screening features

2/4 features avec un lien univarie significatif (p<0.05, sans correction multiple-testing ici -- seulement 4 tests)  _(sans synthese)_

_Statut **OK** · observation 2026-09-29 · moteur `ml` · [donnees](../donnees/screening_features.csv)_


### Couts transaction

7516 predictions, 1513 changements de position (5pb/changement) -- rendement cumule brut=-93.19%, cout total=53.08%, net=-96.80% -- les frais mangent une part importante du rendement (>50% du brut)

_Statut **OK** · observation 2026-09-29 · moteur `ml` · [donnees](../donnees/couts_transaction.csv)_


### Regression multifeatures

coefs (intercept=0.00029, momentum5j=-0.0326, var_vix=0.00027) -- R2 out-of-sample=0.0103 (modele bat la moyenne)

_Statut **OK** · observation 2026-09-29 · moteur `ml` · [donnees](../donnees/regression_multifeatures.csv)_


### Decomposition variance

R² SP500~DGS10 (60j) = 0.2827 -- 28.3% de la variance des rendements SP500 expliquee par les variations du taux 10 ans (le reste = idiosyncratique/autres facteurs)

_Statut **OK** · observation 2026-09-28 · moteur `statistique` · [donnees](../donnees/decomposition_variance.csv)_


### Test chow

test de Chow (taux 10 ans, 1ere vs 2eme moitie des 12 derniers mois) : F=547.278, p=0.0000 -- RUPTURE structurelle significative

_Statut **OK** · observation 2026-09-28 · moteur `statistique` · [donnees](../donnees/test_chow.csv)_


### Arima

ARIMA(1,1,1) sur 100 previsions 1-jour test : RMSE=2.323 vs baseline naive MSE=5.451 -- ARIMA bat la persistance simple

_Statut **OK** · observation 2026-09-30 · moteur `series-temporelles` · [donnees](../donnees/arima.csv)_


### Stacking

poids appris (momentum=-0.082, baseline=0.090, biais=0.090) -- accuracy stacking=0.5459 vs momentum seul=0.5024, baseline seule=0.5459 sur 2255 points test -- stacking NE BAT PAS la baseline, meilleur=stacking / baseline (ex-aequo)

_Statut **OK** · observation 2026-09-29 · moteur `ml` · [donnees](../donnees/stacking.csv)_


### Decision stump

seuil appris=-1.530 (sens=False) -- accuracy stump=0.5455 vs baseline=0.5473 sur 2264 points test -- stump NE BAT PAS la baseline

_Statut **OK** · observation 2026-09-29 · moteur `ml` · [donnees](../donnees/decision_stump.csv)_


### Importance permutation

R2 base=0.0103 -- importance momentum5j=0.00088, importance variation_vix=0.01377 -- VIX plus important

_Statut **OK** · observation 2026-09-29 · moteur `ml` · [donnees](../donnees/importance_permutation.csv)_

