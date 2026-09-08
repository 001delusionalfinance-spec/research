# risque/

Tail risk / détection de saut (ex. Barndorff-Nielsen & Shephard), CoVaR systémique, scénarios
de drawdown. Voir `MAP.md` (racine).

## `modele_var_drawdown.py` (2026-09-08)

VaR et CVaR (Expected Shortfall) historiques — pas paramétriques, ne supposent pas une
distribution normale des rendements (connue pour sous-estimer le risque de queue réel) — à
95% et 99%, sur une fenêtre glissante de 252 jours de S&P 500. Plus le drawdown maximal sur la
même fenêtre.

Testé avec de vraies données, cohérence vérifiée (CVaR toujours pire que la VaR au même seuil,
99% toujours pire que 95%) : VaR95=-1,45%, CVaR95=-1,80%, VaR99=-2,08%, CVaR99=-2,50%,
drawdown max 252j=-9,10%.

Détection de saut (Barndorff-Nielsen & Shephard) volontairement pas construite dans cette
première passe — demande realized variance + bipower variation + tripower quarticity, plus
lourd à valider correctement (GMDC l'a fait en validant d'abord sur données synthétiques à
paramètres connus). À reprendre si utile.

## `modele_skew_kurtosis.py` (2026-09-08)

Skewness et kurtosis en excès (convention Fisher) glissants, 252j — décrit la FORME de la
distribution, pas juste sa queue (VaR/CVaR). Testé réel : skew -0,255 (pertes extrêmes plus
fréquentes que les gains extrêmes), kurtosis +1,205 (queues plus épaisses qu'une gaussienne) —
cohérent avec les faits stylisés connus des rendements actions (Cont 2001).

## `modele_ratios_performance.py` (2026-09-08)

Sharpe, Sortino, Calmar glissants (252j) — lecture de contexte, pas un signal de trade (ce
dépôt ne décide rien, voir `MAP.md`). Taux sans risque supposé nul (simplification documentée).
Testé réel : Sharpe=1,323, Sortino=1,281, Calmar=1,865.

## `modele_covar.py` (2026-09-08)

CoVaR simplifié (Adrian & Brunnermeier 2016, version par quantile plutôt que régression
formelle — documenté comme simplification) : VaR du S&P 500 conditionnelle à un VIX en
détresse (décile le plus haut) vs VaR inconditionnelle. Testé réel, résultat marquant :
VaR95 inconditionnelle=-1,84%, VaR95|VIX détresse=-4,37% (vs -1,52% en régime normal) —
DeltaCoVaR=-2,86pt, l'amplification du risque en stress est réelle et mesurée, pas supposée.

## `modele_stress_test_historique.py` (2026-09-08)

Rejoue l'amplitude relative du pire drawdown de 2008 (GFC, -56,8%) et 2020 (COVID, -33,9%) sur
le niveau actuel du S&P 500. **A nécessité d'étendre `ingestion_yfinance_indices.py` de 2 à
30 ans d'historique** (SP500/VIX seulement — les 10 ETF sectoriels restent à 2 ans, pas de
besoin identifié) — vérifié sans effet négatif sur aucun modèle existant (tous en fenêtre
glissante, ou directement améliorés par plus d'historique, ex. `modele_saisonnalite.py`).

## `modele_sizing_robuste.py` (2026-09-08)

Intervalle de confiance bootstrap (1000 tirages) sur l'estimation de vol réalisée — pas qu'un
point. Testé réel : vol=12,80%, IC90%=[11,62%, 13,99%].

## `modele_nombre_effectif_paris.py` (2026-09-08)

Nombre effectif de paris indépendants (Meucci 2010, entropie de Shannon sur les valeurs propres
de la matrice de corrélation) — 11 marchés COT. Testé réel : 7,14 paris effectifs sur 11 (65%
du maximum théorique).

## `modele_detection_saut.py` (2026-09-08)

Détection de saut (Barndorff-Nielsen & Shephard, tripower quarticity Huang & Tauchen) — promise
depuis la vague 1, construite maintenant. **Limite réelle trouvée en validant sur diffusion pure
synthétique** : 18% de faux positifs à |Z|>1,96 (attendu ~5%), biais de petit échantillon
documenté dans la littérature (n=22 trop petit pour l'asymptotique normale). Testé séparément
sur un saut de 15% injecté : Z=29,75, détecté sans ambiguïté. À lire comme "Z très élevé = saut
quasi certain", pas comme un seuil nominal fiable.

## `modele_choc_taux.py` (2026-09-08)

Sensibilité SP500 à un choc de ±100pb (taux 10 ans), via le beta de
`modele_beta_facteur_macro.py` — **même bug DFF→DGS10 corrigé ici en parallèle** (la version
initiale extrapolait un beta DFF instable à +68,8%/-68,8%, absurde). Testé réel après
correction : +100pb → -7,71% (SP500 7748→7150), économiquement plausible.

## `modele_var_conditionnelle_regime.py` (2026-09-08)

VaR conditionnelle au régime de volatilité actuel (VIX haut vs bas), pas une VaR globale unique.
Testé réel : régime bas actuellement, VaR95 applicable=-1,14% (vs -1,84% non-conditionnelle).

## `modele_ratios_conditionnels_regime.py` (2026-09-08, vague 7)

Sharpe/Sortino conditionnels au régime de volatilité (VIX haut/bas), même logique de
conditionnement que `modele_var_conditionnelle_regime.py` mais appliquée aux ratios de
performance plutôt qu'à la VaR. Testé réel : Sharpe régime haut-vol=-1,107, bas-vol=2,418,
global=0,427 — écart marqué entre régimes, un Sharpe global masque une réalité très différente
selon le contexte de volatilité.

## `modele_choc_vol_parametrique.py` (2026-09-08, vague 7)

VaR paramétrique (gaussienne, quantile Z_95=1,645) sous des chocs de volatilité multiplicatifs
(x1/x2/x3) — complète `modele_choc_taux.py` (choc sur les taux) avec un choc directement sur la
vol. Testé réel : choc x1 → VaR95=-1,26%/jour, x2 → -2,59%, x3 → -3,91% (relation
quasi-linéaire attendue pour une VaR paramétrique gaussienne).
