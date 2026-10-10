# Positionnement et comportement

COT, crowding, devises, courbe, extremes et divergences entre prix et positions.

Mis a jour : **2026-10-10 09:58 UTC** · 15 lectures.

[Retour au tableau de bord](../README.md)

### Positionnement courbe taux

8 contrats de taux -- pari de NIVEAU -- courtes et longues sont short, le marche joue un deplacement de toute la courbe dans le meme sens. Positionnement a un extreme historique sur : Fed funds (extreme haut, 89e pct), SOFR 3 mois (extreme bas, 7e pct), 10 ans (extreme bas, 12e pct)

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_courbe_taux.csv) · [graphique](../graphiques/positionnement_courbe_taux/apercu.png)_


### Positionnement devises

8 devises (net positif = pari haussier sur la devise etrangere, jamais sur le dollar) -- aucune position de carry identifiee. A un extreme historique : Yen (extreme haut, 96e pct), Euro (extreme bas, 13e pct), Dollar canadien (extreme bas, 8e pct), Livre sterling (extreme bas, 1e pct), Dollar australien (extreme bas, 1e pct) -- un positionnement extreme est vulnerable a un deboucle rapide si la volatilite monte

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_devises.csv) · [graphique](../graphiques/positionnement_devises/apercu.png)_


### Positionnement cot

WTI_CRUDE : net=99060.0, z=-0.62, extreme=False  _(sans synthese)_

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_cot.csv) · [graphique](../graphiques/positionnement_cot/positionnement_cot.png)_


### Momentum positionnement

WTI_CRUDE : z=-0.62 (il y a 8sem: -0.68), momentum=+0.07 -- positionnement se degonfle (l'extreme diminue)  _(sans synthese)_

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/momentum_positionnement.csv)_


### Crowding cross asset

10/32 marches avec |z|>=1.5 simultanement : CORN(+1.74);EUR_FX(-2.41);GBP_FX(-1.57);MXN_FX(-3.54);NASDAQ_MINI(+1.81);NAT_GAS(-2.00);RUSSELL_MINI(-1.79);SOYBEANS(+1.59);UST_2Y(+2.10);UST_5Y(+1.52)

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/crowding_cross_asset.csv) · [graphique](../graphiques/crowding_cross_asset/apercu.png)_


### Divergence cot prix

SP500 +2.29% sur 30j, COT net -75941 -> -154070 -- DIVERGENCE (prix monte, positionnement recule)

_Statut **OK** · observation 2026-10-09 · moteur `positionnement-comportemental` · [donnees](../donnees/divergence_cot_prix.csv)_


### Ratio commercial speculatif

WTI_CRUDE : commercial=-126458, speculatif=+99060, ratio=1.28, sens_oppose=True  _(sans synthese)_

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/ratio_commercial_speculatif.csv)_


### Rotation risk on off

z-score moyen risque=+0.60 ({'SP500_EMINI': -0.6160138596634153, 'NASDAQ_MINI': 1.809370481929021}), refuge=-0.28 ({'GOLD': 0.3250548572181775, 'UST_10Y': -0.8781074587989088}) -- posture=risk-on

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/rotation_risk_on_off.csv)_


### Concentration traders

WTI_CRUDE : 298 traders, position nette moyenne/trader=332 -- diffus (large base de traders) (mediane du groupe : 453)  _(sans synthese)_

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/concentration_traders.csv)_


### Metaux precieux

z-scores : {'GOLD': 0.3250548572181775, 'SILVER': -0.9272943991568718, 'PLATINUM': -0.679711225452267} -- SILVER le plus tendu, sans franchir le seuil extreme (|z|>2) -- ecart or/industriels=+1.13

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/metaux_precieux.csv)_


### Persistance extremes

32 marches analyses, plus longue persistance : SOFR_3M (23 semaines)

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/persistance_extremes.csv)_


### Correlations positionnement

254/496 paires significatives apres correction Bonferroni (alpha=0.05/496)  _(sans synthese)_

_Statut **OK** · observation non exposee par la sortie · moteur `statistique` · [donnees](../donnees/correlations_positionnement.csv)_


### Dollar smile

USD_INDEX net=+12011 (long), 2/3 devises non-USD nettes courtes -- positionnement coherent

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/dollar_smile.csv)_


### Extremes historiques

32 marches -- le plus proche de son record directionnel : NASDAQ_MINI (100% de son record)

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/extremes_historiques.csv)_


### Correlation cot prix

correlation COT/prix SP500 (26 semaines) = +0.140 -- lien faible

_Statut **OK** · observation 2026-10-06 · moteur `positionnement-comportemental` · [donnees](../donnees/correlation_cot_prix.csv)_

