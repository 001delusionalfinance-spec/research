# series-temporelles/

Regime-switching formel (HMM/Kalman, pas juste un seuil sur percentile), volatilité
conditionnelle (GARCH), saisonnalité. Voir `MAP.md` (racine).

## `modele_volatilite_ewma.py` (2026-09-08)

Volatilité réalisée S&P 500 (5/20/60j) + volatilité EWMA (RiskMetrics, lambda=0.94, poids
décroissant exponentiellement — plus réactive à un choc récent qu'une fenêtre fixe). Tendance
mesurée sur les 10 derniers runs accumulés dans `rapports/donnees/` (10% de variation relative,
pas un seuil absolu).

Nécessite `ingestion_yfinance_indices.py` (SP500, VIX — même pattern d'appel direct à l'API
chart Yahoo, vérifié fonctionnel et frais le 2026-09-08).

Testé avec de vraies données (vol réalisée 60j ≈ 11,8%, EWMA ≈ 10,4%, cohérent avec un VIX à
~15 le même jour) et la logique de classification de tendance testée sur des cas synthétiques
à résultat connu (hausse/stable/baisse) avant le test réel.

## `modele_garch.py` (2026-09-08)

GARCH(1,1) sur les rendements S&P 500 (librairie `arch`) — paramètres estimés par maximum de
vraisemblance, pas un lambda fixé comme l'EWMA. Piège connu et vérifié explicitement : la
librairie recommande des rendements ×100 pour la stabilité numérique, oublier de re-diviser
donne une vol ~100x trop grande (bug réel classique — évité
ici en comparant le résultat à la vol réalisée). Testé réel : 12,10% annualisée, persistance
0,921 — cohérent avec EWMA/réalisée.

## `modele_hurst.py` (2026-09-08)

Exposant de Hurst (analyse R/S, Mandelbrot 1968) — mesure si les rendements ont une mémoire
longue (H>0,5, tendanciel) ou courte (H<0,5, retour à la moyenne). **Limite réelle trouvée en
validant sur une marche aléatoire synthétique** (H théorique = 0,5) : le R/S simple a un biais
positif connu à échantillon fini, confirmé ici (H mesuré = 0,593 sur du vrai bruit gaussien).
Le résultat réel sur S&P 500 (H=0,608 sur 2 ans ; recalculé à 0,554 depuis l'extension à 30 ans
d'historique, plus proche du biais mesuré) est donc à peine au-dessus de ce biais — preuve de
mémoire plus faible que le chiffre brut ne le suggère.

## `modele_ornstein_uhlenbeck_vix.py` (2026-09-08)

Retour à la moyenne (processus OU, version discrète = régression variation ~ niveau) sur le
VIX — contrairement au S&P 500 (marche quasi aléatoire, cf. Hurst ci-dessus), le VIX est
l'exemple manuel du mean-reverting en finance. **Estimateur validé sur processus OU synthétique
à paramètres connus** (theta=0,1 → estimé 0,091 ; mu=20,0 → estimé 20,17) avant le test réel.
Testé réel : VIX actuel=15,31, niveau moyen estimé=18,45, demi-vie=7,0 jours.

## `modele_changepoint_volatilite.py` (2026-09-08)

Détection de rupture (segmentation binaire à un point, pas PELT — plus simple, validée sur cas
synthétique à rupture connue avant le réel) sur le niveau de volatilité S&P 500. Depuis
l'extension à 30 ans d'historique, détecte désormais une vraie rupture historiquement
significative plutôt qu'un artefact récent : rupture le 2011-12-21 (fin de la crise de la dette
européenne), vol avant=21,3%, après=16,7%.

## `modele_kalman_niveau_local.py` (2026-09-08)

Filtre de Kalman (modèle à niveau local, `statsmodels.UnobservedComponents`) sur le VIX — lissage
bayésien mis à jour à chaque observation, pas une moyenne mobile à fenêtre fixe. Testé réel :
VIX observé=15,28, filtré=15,27.

## `modele_hp_filter_taux.py` (2026-09-08)

Décomposition tendance/cycle (filtre Hodrick-Prescott, lambda=129600 pour données quotidiennes,
Ravn & Uhlig 2002) sur le taux 10 ans US. Testé réel : écart cyclique quasi nul (+0,02pt),
proche de sa tendance locale.

## `modele_var_sp500_vix.py` (2026-09-08)

VAR (Vector Autoregression, ordre choisi par AIC via statsmodels) sur [rendement SP500,
variation VIX] — système dynamique complet, pas juste un test de causalité pairwise (déjà fait).
**Bug réel trouvé en testant** : `.iloc` sur un `ndarray` numpy brut (pas un DataFrame pandas) —
corrigé avec une indexation numpy standard. Testé réel : ordre AIC=10, coefficients réels
obtenus.

## `modele_analyse_spectrale.py` (2026-09-08)

Périodogramme (FFT) sur les rendements du VIX — cherche des cycles dominants au-delà du retour
à la moyenne déjà mesuré (Ornstein-Uhlenbeck). Testé réel : 3 périodes dominantes à 2,2/5,4/4,0
jours — pas de cycle mensuel/trimestriel net détecté, résultat honnête.

## `modele_arima.py` (2026-09-08)

ARIMA(1,1,1) sur le VIX, prévision walk-forward 1-jour (statsmodels, ré-ajusté à chaque pas,
pas un fit unique). Testé réel : RMSE=2,259 vs MSE naïf=5,283 — ARIMA bat la persistance
simple.

## `modele_decomposition_stl.py` (2026-09-08, vague 7)

Décomposition STL (Seasonal-Trend decomposition using Loess) du VIX, période=5 (semaine
boursière) — sépare tendance, composante saisonnière hebdomadaire et résidu, distinct du
spectre FFT déjà mesuré (ici on isole spécifiquement une saisonnalité connue a priori, pas une
recherche de cycle inconnu). Testé réel : tendance=15,01, composante saisonnière=+0,627,
résidu=-0,107 — la saisonnalité hebdomadaire explique 0,69% de la variance totale du VIX
(négligeable), résultat honnête.

## `modele_ornstein_uhlenbeck_credit.py` (2026-09-08, vague 7)

Retour à la moyenne (Ornstein-Uhlenbeck) appliqué au spread de crédit high-yield
(`BAMLH0A0HYM2`), même estimateur que `modele_ornstein_uhlenbeck_vix.py` mais sur une série
économiquement différente (spread de crédit vs volatilité implicite). Testé réel : spread HY
actuel=2,68, niveau moyen estimé=3,03, demi-vie=48,0 jours, écart actuel=-0,35 (spread
actuellement en-dessous de sa moyenne long terme).
