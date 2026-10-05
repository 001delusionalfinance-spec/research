# Positionnement et comportement

COT, crowding, devises, courbe, extremes et divergences entre prix et positions.

Mis a jour : **2026-10-05 11:43 UTC** · 15 lectures.

[Retour au tableau de bord](../README.md)

### Positionnement courbe taux

8 contrats de taux -- pari de NIVEAU -- courtes et longues sont short, le marche joue un deplacement de toute la courbe dans le meme sens. Positionnement a un extreme historique sur : SOFR 3 mois (extreme bas, 6e pct), 10 ans (extreme bas, 11e pct), Bond (30 ans) (extreme bas, 8e pct)

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_courbe_taux.csv) · [graphique](../graphiques/positionnement_courbe_taux/apercu.png)_


### Positionnement devises

8 devises (net positif = pari haussier sur la devise etrangere, jamais sur le dollar) -- aucune position de carry identifiee. A un extreme historique : Yen (extreme haut, 93e pct), Dollar australien (extreme bas, 12e pct), Dollar canadien (extreme bas, 9e pct), Livre sterling (extreme bas, 2e pct) -- un positionnement extreme est vulnerable a un deboucle rapide si la volatilite monte

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_devises.csv) · [graphique](../graphiques/positionnement_devises/apercu.png)_


### Positionnement cot

WTI_CRUDE : net=109463.0, z=-0.43, extreme=False  _(sans synthese)_

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/positionnement_cot.csv) · [graphique](../graphiques/positionnement_cot/positionnement_cot.png)_


### Momentum positionnement

WTI_CRUDE : z=-0.43 (il y a 8sem: -0.46), momentum=+0.03 -- positionnement se degonfle (l'extreme diminue)  _(sans synthese)_

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/momentum_positionnement.csv)_


### Crowding cross asset

9/32 marches avec |z|>=1.5 simultanement : COPPER(+1.71);CORN(+2.08);EUR_FX(-1.99);NASDAQ_MINI(+1.52);NAT_GAS(-1.95);RUSSELL_MINI(-1.50);SOFR_3M(-1.57);UST_2Y(+2.49);UST_5Y(+1.90)

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/crowding_cross_asset.csv) · [graphique](../graphiques/crowding_cross_asset/apercu.png)_


### Divergence cot prix

SP500 +0.73% sur 30j, COT net -67994 -> -142499 -- DIVERGENCE (prix monte, positionnement recule)

_Statut **OK** · observation 2026-10-02 · moteur `positionnement-comportemental` · [donnees](../donnees/divergence_cot_prix.csv)_


### Ratio commercial speculatif

WTI_CRUDE : commercial=-142618, speculatif=+109463, ratio=1.30, sens_oppose=True  _(sans synthese)_

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/ratio_commercial_speculatif.csv)_


### Rotation risk on off

z-score moyen risque=+0.55 ({'SP500_EMINI': -0.4267883179141355, 'NASDAQ_MINI': 1.5220931196458065}), refuge=-0.13 ({'GOLD': 0.5924661545566637, 'UST_10Y': -0.8566067063170019}) -- posture=risk-on

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/rotation_risk_on_off.csv)_


### Concentration traders

WTI_CRUDE : 304 traders, position nette moyenne/trader=360 -- diffus (large base de traders) (mediane du groupe : 401)  _(sans synthese)_

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/concentration_traders.csv)_


### Metaux precieux

z-scores : {'GOLD': 0.5924661545566637, 'SILVER': -1.028066986772358, 'PLATINUM': -0.6756327819342007} -- SILVER le plus tendu, sans franchir le seuil extreme (|z|>2) -- ecart or/industriels=+1.44

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/metaux_precieux.csv)_


### Persistance extremes

32 marches analyses, plus longue persistance : SOFR_3M (22 semaines)

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/persistance_extremes.csv)_


### Correlations positionnement

254/496 paires significatives apres correction Bonferroni (alpha=0.05/496)  _(sans synthese)_

_Statut **OK** · observation non exposee par la sortie · moteur `statistique` · [donnees](../donnees/correlations_positionnement.csv)_


### Dollar smile

USD_INDEX net=+11881 (long), 2/3 devises non-USD nettes courtes -- positionnement coherent

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/dollar_smile.csv)_


### Extremes historiques

32 marches -- le plus proche de son record directionnel : NAT_GAS (100% de son record)

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/extremes_historiques.csv)_


### Correlation cot prix

correlation COT/prix SP500 (26 semaines) = +0.068 -- lien faible

_Statut **OK** · observation 2026-09-29 · moteur `positionnement-comportemental` · [donnees](../donnees/correlation_cot_prix.csv)_

