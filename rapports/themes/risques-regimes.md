# Risques, volatilite et regimes

Volatilite, queues, drawdowns, stress, contagion et changements de regime.

Mis a jour : **2026-09-26 18:09 UTC** · 23 lectures.

[Retour au tableau de bord](../README.md)

### Vol cross asset

6 mesures de volatilite : Petrole (OVX) 88e pct, Or (GVZ) 80e pct, Taux US (MOVE) 43e pct, Nasdaq (VXN) 38e pct, Vol de la vol (VVIX) 27e pct, Actions US (VIX) 21e pct -- stress LOCALISE sur Petrole (OVX), Or (GVZ) pendant que le reste ne l'est pas -- episode propre a cette classe d'actifs, pas une aversion au risque d'ensemble

_Statut **OK** · observation 2026-09-25 · moteur `risque` · [donnees](../donnees/vol_cross_asset.csv) · [graphique](../graphiques/vol_cross_asset/apercu.png)_


### Volatilite ewma

vol realisee 60j=0.11153026065780319, EWMA=0.1081 (tendance 10 runs: stable)

_Statut **OK** · observation 2026-09-25 · moteur `series-temporelles` · [donnees](../donnees/volatilite_ewma.csv) · [graphique](../graphiques/volatilite_ewma/volatilite_ewma.png)_


### Garch

vol GARCH(1,1) annualisee=0.1233 (alpha=0.114, beta=0.868, persistance=0.983 -- tres proche de 1 -- chocs de volatilite tres durables)

_Statut **OK** · observation 2026-09-25 · moteur `series-temporelles` · [donnees](../donnees/garch.csv) · [graphique](../graphiques/garch/apercu.png)_


### Hurst

Hurst=0.5535 (R2 regression=1.000) -- persistant (tendanciel)

_Statut **OK** · observation 2026-09-25 · moteur `series-temporelles` · [donnees](../donnees/hurst.csv)_


### Ornstein uhlenbeck vix

VIX actuel=14.87, niveau moyen estime (mu)=20.20, demi-vie=28.8j, ecart actuel=-5.33 -- VIX actuel en-dessous de son niveau moyen de long terme

_Statut **OK** · observation 2026-09-25 · moteur `series-temporelles` · [donnees](../donnees/ornstein_uhlenbeck_vix.csv) · [graphique](../graphiques/ornstein_uhlenbeck_vix/apercu.png)_


### Changepoint volatilite

rupture detectee le 2011-12-21 -- vol avant=0.2129, vol apres=0.1666 (reduction SSE=0.5%) -- baisse de la vol au point de rupture (-21.7%)

_Statut **OK** · observation 2026-09-25 · moteur `series-temporelles` · [donnees](../donnees/changepoint_volatilite.csv)_


### Kalman niveau local

VIX observe=14.87, filtre Kalman=14.98 (ecart-type=0.62), ratio signal/bruit=0.2051 -- le filtre lisse fortement le bruit, reagit lentement (ecart obs.-filtre=-0.11)

_Statut **OK** · observation 2026-09-25 · moteur `series-temporelles` · [donnees](../donnees/kalman_niveau_local.csv)_


### Var sp500 vix

VAR ordre choisi par AIC=10 -- coef SP500(t-1)->VIX(t)=0.3769116249569233 (SP500(t-1) en hausse -> VIX(t) tend aussi a monter), coef VIX(t-1)->SP500(t)=-0.05237241130035915 (VIX(t-1) en hausse -> SP500(t) tend a baisser)

_Statut **OK** · observation 2026-09-25 · moteur `series-temporelles` · [donnees](../donnees/var_sp500_vix.csv)_


### Analyse spectrale

3 periodes dominantes (jours de bourse) : [2.2, 4.0, 5.3] -- cycle(s) connu(s) qui ressortent : 4.0j~hebdomadaire, 5.3j~hebdomadaire

_Statut **OK** · observation 2026-09-25 · moteur `series-temporelles` · [donnees](../donnees/analyse_spectrale.csv)_


### Var drawdown

VaR95=-1.45% CVaR95=-1.80% VaR99=-2.08% CVaR99=-2.50% drawdown_max_252j=-9.10% -- soit l'equivalent de ~6 jours de VaR95 d'affilee

_Statut **OK** · observation 2026-09-25 · moteur `risque` · [donnees](../donnees/var_drawdown.csv) · [graphique](../graphiques/var_drawdown/apercu.png)_


### Skew kurtosis

skewness=-0.201 (asymetrie negative (pertes extremes > gains extremes)), kurtosis exces=+1.031 (queues epaisses (risque extreme sous-estime par une hypothese normale))

_Statut **OK** · observation 2026-09-25 · moteur `risque` · [donnees](../donnees/skew_kurtosis.csv)_


### Ratios performance

Sharpe=1.230 (bon), Sortino=1.207 (bon), Calmar=1.755 (bon) -- lecture sur fenetre 252j (~1 an, echantillon limite), seuils academiques standards, taux sans risque suppose nul

_Statut **OK** · observation 2026-09-25 · moteur `risque` · [donnees](../donnees/ratios_performance.csv)_


### Covar

VaR95 inconditionnelle=-1.84%, VaR95|VIX detresse(>=29.5)=-4.37%, VaR95|VIX normal=-1.52% -- DeltaCoVaR=-2.86pt (755 jours de detresse dans l'echantillon) -- contagion notable -- VaR 2.9x plus severe en detresse

_Statut **OK** · observation 2026-09-25 · moteur `risque` · [donnees](../donnees/covar.csv)_


### Stress test historique

COVID_2020 (2020-02-19 -> 2020-03-23) : chute historique=-33.9% -- rejouee sur le niveau actuel (7743) -> 5116  _(sans synthese)_

_Statut **OK** · observation 2026-09-25 · moteur `risque` · [donnees](../donnees/stress_test_historique.csv) · [graphique](../graphiques/stress_test_historique/apercu.png)_


### Sizing robuste

vol point estimate=0.1297, IC90%=[0.1184, 0.1411] (1000 tirages bootstrap) -- intervalle etroit (17% du point estimate) -- estimation relativement fiable

_Statut **OK** · observation 2026-09-25 · moteur `risque` · [donnees](../donnees/sizing_robuste.csv)_


### Nombre effectif paris

32 marches, nombre effectif de paris independants=13.45 (42% du maximum theorique de 32) -- moderement concentre -- redondance significative entre plusieurs paris

_Statut **OK** · observation 2026-09-22 · moteur `risque` · [donnees](../donnees/nombre_effectif_paris.csv)_


### Detection saut

Z-stat BNS (fenetre 22j)=1.336 (seuil ±1.96) -- pas de saut isole detecte

_Statut **OK** · observation 2026-09-25 · moteur `risque` · [donnees](../donnees/detection_saut.csv)_


### Choc taux

beta SP500/DGS10=-0.0790 -- choc +100pb : -7.90% (SP500 7704 -> 7096) ; choc -100pb : +7.90% (-> 8313)

_Statut **OK** · observation 2026-09-24 · moteur `risque` · [donnees](../donnees/choc_taux.csv)_


### Qualite regime macro

instabilite taux=0.0088, instabilite VIX=0.0679 -- score qualite du regime=-0.0383 (plus haut = regime plus stable/previsible)

_Statut **OK** · observation 2026-09-24 · moteur `factorielle` · [donnees](../donnees/qualite_regime_macro.csv)_


### Var conditionnelle regime

regime VIX actuel=bas (rang percentile=32) -- VaR95 applicable maintenant=-1.14% (vs VaR95 globale non-conditionnelle=-1.84%)

_Statut **OK** · observation 2026-09-25 · moteur `risque` · [donnees](../donnees/var_conditionnelle_regime.csv)_


### Decomposition stl

VIX : tendance=15.52, composante saisonniere (periode 5j)=-0.665, residu=+0.016 -- la saisonnalite explique 0.71% de la variance totale (negligeable)

_Statut **OK** · observation 2026-09-25 · moteur `series-temporelles` · [donnees](../donnees/decomposition_stl.csv) · [graphique](../graphiques/decomposition_stl/apercu.png)_


### Ratios conditionnels regime

Sharpe regime haut-vol=-1.107, bas-vol=2.406, global=0.423 -- meilleur en regime calme, comme attendu

_Statut **OK** · observation 2026-09-25 · moteur `risque` · [donnees](../donnees/ratios_conditionnels_regime.csv)_


### Choc vol parametrique

vol actuelle=12.97%, scenarios x1/x2/x3 calcules -- pire scenario (x3) = -3.97%/jour, soit 3.1x le scenario de base

_Statut **OK** · observation 2026-09-25 · moteur `risque` · [donnees](../donnees/choc_vol_parametrique.csv)_

