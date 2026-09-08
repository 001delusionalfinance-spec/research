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
