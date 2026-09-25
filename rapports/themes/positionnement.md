# Positionnement et comportement

COT, crowding, devises, courbe, extremes et divergences entre prix et positions.

Mis a jour : **2026-09-25 08:26 UTC** · 15 lectures.

[Retour au tableau de bord](../README.md)

### Positionnement courbe taux

8 contrats de taux -- pari de NIVEAU -- courtes et longues sont short, le marche joue un deplacement de toute la courbe dans le meme sens. Positionnement a un extreme historique sur : SOFR 3 mois (extreme bas, 2e pct), Bond (30 ans) (extreme bas, 2e pct)

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_courbe_taux.csv) · [graphique](../graphiques/positionnement_courbe_taux/apercu.png)_


### Positionnement devises

8 devises (net positif = pari haussier sur la devise etrangere, jamais sur le dollar) -- aucune position de carry identifiee. A un extreme historique : Yen (extreme haut, 98e pct), Dollar neo-zelandais (extreme haut, 97e pct), Livre sterling (extreme bas, 14e pct), Franc suisse (extreme bas, 12e pct) -- un positionnement extreme est vulnerable a un deboucle rapide si la volatilite monte

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_devises.csv) · [graphique](../graphiques/positionnement_devises/apercu.png)_


### Positionnement cot

WTI_CRUDE : net=135905.0, z=0.04, extreme=False  _(sans synthese)_

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_cot.csv) · [graphique](../graphiques/positionnement_cot/positionnement_cot.png)_


### Momentum positionnement

WTI_CRUDE : z=+0.04 (il y a 8sem: -1.04), momentum=+1.08 -- positionnement se degonfle (l'extreme diminue)  _(sans synthese)_

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/momentum_positionnement.csv)_


### Crowding cross asset

11/32 marches avec |z|>=1.5 simultanement : CORN(+2.45);EUR_FX(-1.57);NAT_GAS(-1.85);NZD_FX(+2.22);SOFR_3M(-2.07);SOYBEANS(+1.58);UST_2Y(+2.37);UST_5Y(+2.06);UST_BOND(-1.76);UST_ULTRA_BOND(-1.83);WHEAT(+1.61)

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/crowding_cross_asset.csv) · [graphique](../graphiques/crowding_cross_asset/apercu.png)_


### Divergence cot prix

SP500 +0.35% sur 30j, COT net 11280 -> -100461 -- DIVERGENCE (prix monte, positionnement recule)

_Statut **OK** · observation 2026-09-24 · moteur `positionnement-comportemental` · [donnees](../donnees/divergence_cot_prix.csv)_


### Ratio commercial speculatif

WTI_CRUDE : commercial=-164858, speculatif=+135905, ratio=1.21, sens_oppose=True  _(sans synthese)_

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/ratio_commercial_speculatif.csv)_


### Rotation risk on off

z-score moyen risque=+0.49 ({'SP500_EMINI': 0.2781561647249375, 'NASDAQ_MINI': 0.7113876667331047}), refuge=+0.46 ({'GOLD': 0.9287746611732994, 'UST_10Y': -0.004638865300170082}) -- posture=mixte/neutre

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/rotation_risk_on_off.csv)_


### Concentration traders

WTI_CRUDE : 326 traders, position nette moyenne/trader=417 -- diffus (large base de traders) (mediane du groupe : 418)  _(sans synthese)_

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/concentration_traders.csv)_


### Metaux precieux

z-scores : {'GOLD': 0.9287746611732994, 'SILVER': -0.8411389470660166, 'PLATINUM': -0.2805751279778128} -- GOLD le plus tendu, sans franchir le seuil extreme (|z|>2) -- ecart or/industriels=+1.49

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/metaux_precieux.csv)_


### Persistance extremes

32 marches analyses, plus longue persistance : SOFR_3M (20 semaines)

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/persistance_extremes.csv)_


### Correlations positionnement

256/496 paires significatives apres correction Bonferroni (alpha=0.05/496)  _(sans synthese)_

_Statut **OK** · observation non exposee par la sortie · moteur `statistique` · [donnees](../donnees/correlations_positionnement.csv)_


### Dollar smile

USD_INDEX net=+10593 (long), 2/3 devises non-USD nettes courtes -- positionnement coherent

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/dollar_smile.csv)_


### Extremes historiques

32 marches -- le plus proche de son record directionnel : NAT_GAS (100% de son record)

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/extremes_historiques.csv)_


### Correlation cot prix

correlation COT/prix SP500 (26 semaines) = +0.025 -- lien faible

_Statut **OK** · observation 2026-09-15 · moteur `positionnement-comportemental` · [donnees](../donnees/correlation_cot_prix.csv)_

