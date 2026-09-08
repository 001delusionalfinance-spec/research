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
