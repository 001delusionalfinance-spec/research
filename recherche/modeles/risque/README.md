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
