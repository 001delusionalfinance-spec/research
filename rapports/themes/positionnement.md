# Positionnement et comportement

COT, crowding, devises, courbe, extremes et divergences entre prix et positions.

Mis a jour : **2026-09-28 05:32 UTC** · 15 lectures.

[Retour au tableau de bord](../README.md)

### Positionnement courbe taux

8 contrats de taux -- pari de NIVEAU -- courtes et longues sont short, le marche joue un deplacement de toute la courbe dans le meme sens. Positionnement a un extreme historique sur : SOFR 3 mois (extreme bas, 5e pct)

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_courbe_taux.csv) · [graphique](../graphiques/positionnement_courbe_taux/apercu.png)_


### Positionnement devises

8 devises (net positif = pari haussier sur la devise etrangere, jamais sur le dollar) -- aucune position de carry identifiee. A un extreme historique : Yen (extreme haut, 97e pct), Franc suisse (extreme bas, 14e pct), Livre sterling (extreme bas, 2e pct) -- un positionnement extreme est vulnerable a un deboucle rapide si la volatilite monte

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_devises.csv) · [graphique](../graphiques/positionnement_devises/apercu.png)_


### Positionnement cot

WTI_CRUDE : net=141106.0, z=0.15, extreme=False  _(sans synthese)_

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_cot.csv) · [graphique](../graphiques/positionnement_cot/positionnement_cot.png)_


### Momentum positionnement

WTI_CRUDE : z=+0.15 (il y a 8sem: -0.35), momentum=+0.49 -- positionnement se degonfle (l'extreme diminue)  _(sans synthese)_

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/momentum_positionnement.csv)_


### Crowding cross asset

11/32 marches avec |z|>=1.5 simultanement : BRENT_CRUDE(-1.69);COPPER(+2.02);CORN(+2.31);EUR_FX(-1.90);NASDAQ_MINI(+1.82);NAT_GAS(-1.67);SOFR_3M(-1.73);SOYBEANS(+1.75);UST_2Y(+2.01);UST_5Y(+2.20);UST_ULTRA_BOND(-1.58)

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/crowding_cross_asset.csv) · [graphique](../graphiques/crowding_cross_asset/apercu.png)_


### Divergence cot prix

SP500 +0.88% sur 30j, COT net -10560 -> -133228 -- DIVERGENCE (prix monte, positionnement recule)

_Statut **OK** · observation 2026-09-25 · moteur `positionnement-comportemental` · [donnees](../donnees/divergence_cot_prix.csv)_


### Ratio commercial speculatif

WTI_CRUDE : commercial=-169889, speculatif=+141106, ratio=1.20, sens_oppose=True  _(sans synthese)_

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/ratio_commercial_speculatif.csv)_


### Rotation risk on off

z-score moyen risque=+0.77 ({'SP500_EMINI': -0.28249477882517304, 'NASDAQ_MINI': 1.8208598917628376}), refuge=+0.45 ({'GOLD': 0.8076914537111165, 'UST_10Y': 0.0983803955037745}) -- posture=mixte/neutre

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/rotation_risk_on_off.csv)_


### Concentration traders

WTI_CRUDE : 312 traders, position nette moyenne/trader=452 -- concentre (peu de mains) (mediane du groupe : 423)  _(sans synthese)_

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/concentration_traders.csv)_


### Metaux precieux

z-scores : {'GOLD': 0.8076914537111165, 'SILVER': -0.8121496674542396, 'PLATINUM': -0.2532302108462876} -- SILVER le plus tendu, sans franchir le seuil extreme (|z|>2) -- ecart or/industriels=+1.34

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/metaux_precieux.csv)_


### Persistance extremes

32 marches analyses, plus longue persistance : SOFR_3M (21 semaines)

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/persistance_extremes.csv)_


### Correlations positionnement

256/496 paires significatives apres correction Bonferroni (alpha=0.05/496)  _(sans synthese)_

_Statut **OK** · observation non exposee par la sortie · moteur `statistique` · [donnees](../donnees/correlations_positionnement.csv)_


### Dollar smile

USD_INDEX net=+10330 (long), 2/3 devises non-USD nettes courtes -- positionnement coherent

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/dollar_smile.csv)_


### Extremes historiques

32 marches -- le plus proche de son record directionnel : SOYBEANS (100% de son record)

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/extremes_historiques.csv)_


### Correlation cot prix

correlation COT/prix SP500 (26 semaines) = +0.000 -- lien faible

_Statut **OK** · observation 2026-09-22 · moteur `positionnement-comportemental` · [donnees](../donnees/correlation_cot_prix.csv)_

