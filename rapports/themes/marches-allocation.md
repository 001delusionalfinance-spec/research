# Marches, facteurs et allocation

Change, actions, secteurs, facteurs, rotations et signaux d'allocation.

Mis a jour : **2026-10-09 17:09 UTC** · 16 lectures.

[Retour au tableau de bord](../README.md)

### Reer us

REER US=108.25 (rang percentile=94, variation YoY=+0.90%) -- dollar reel fort (competitivite reduite)

_Statut **OK** · observation 2026-07-01 · moteur `macro` · [donnees](../donnees/reer_us.csv)_


### Differentiel taux change

8 paires testees sur variations a 21 jours -- le lien taux/change tient sur 6 paire(s) apres correction pour tests multiples : EURUSD, USDJPY, USDCAD, USDSEK, EURJPY, EURGBP

_Statut **OK** · observation 2026-10-07 · moteur `statistique` · [donnees](../donnees/differentiel_taux_change.csv)_


### Indices mondiaux

7 indices (devise locale) : Coree (KOSPI) +86.7% en tete sur 12 mois, Hong Kong (Hang Seng) -11.3% en queue -- ecart tres large entre blocs sur 12 mois (98pt) -- les cycles economiques ou les flux divergent nettement. ROTATION en cours : Coree (KOSPI) mene sur 12 mois mais Etats-Unis (S&P 500) a repris la tete sur 3 mois

_Statut **OK** · observation 2026-10-09 · moteur `factorielle` · [donnees](../donnees/indices_mondiaux.csv) · [graphique](../graphiques/indices_mondiaux/apercu.png)_


### Correlation glissante

correlation glissante 60j SP500/VIX = -0.738 (min=-0.955, max=-0.429 sur la fenetre d'historique disponible) -- dans la zone intermediaire de sa fourchette historique

_Statut **OK** · observation 2026-10-09 · moteur `statistique` · [donnees](../donnees/correlation_glissante.csv) · [graphique](../graphiques/correlation_glissante/correlation_glissante_sp500_vix.png)_


### Clustering marches

32 marches, 4 clusters (average linkage, distance=1-|r|) : cluster 1 : ['AUD_FX', 'BRENT_CRUDE', 'CAD_FX', 'CHF_FX', 'COPPER', 'GOLD', 'JPY_FX', 'MXN_FX', 'NASDAQ_MINI', 'NZD_FX', 'RUSSELL_MINI', 'SILVER', 'USD_INDEX', 'UST_10Y', 'UST_2Y', 'UST_5Y', 'UST_ULTRA_10Y', 'UST_ULTRA_BOND', 'VIX_FUT', 'WHEAT', 'WTI_CRUDE'] | cluster 2 : ['CORN', 'GBP_FX', 'NAT_GAS', 'PALLADIUM', 'PLATINUM', 'SOFR_3M', 'SOYBEANS'] | cluster 3 : ['EUR_FX', 'SP500_EMINI'] | cluster 4 : ['FED_FUNDS', 'UST_BOND']

_Statut **OK** · observation 2026-09-29 · moteur `statistique` · [donnees](../donnees/clustering_marches.csv)_


### Beta facteur macro

beta SP500/DGS10 (60j) = -0.0736 (rendement SP500 pour +1pt de taux 10 ans, 57/60 jours avec variation reelle) -- sensibilite elevee au facteur macro (choc de +100pb extrapole = -7.1%)

_Statut **OK** · observation 2026-10-07 · moteur `statistique` · [donnees](../donnees/beta_facteur_macro.csv)_


### Momentum prix

SP500 momentum 12-1 mois = 13.38% -- haussier (momentum positif), detail 1/3/6/12m = [2.28, 3.1, 14.57, 15.96]

_Statut **OK** · observation 2026-10-09 · moteur `factorielle` · [donnees](../donnees/momentum_prix.csv)_


### Carry proxy

Chine : 1.54% vs US 3.88% -- diff=-2.34pt (carry negatif (taux < US))  _(sans synthese)_

_Statut **OK** · observation 2026-10-07 · moteur `factorielle` · [donnees](../donnees/carry_proxy.csv)_


### Beta vol

beta SP500/VIX (60j) = -0.00495 (rendement SP500 pour +1pt VIX) -- sensibilite normale, relation inverse attendue (normale)

_Statut **OK** · observation 2026-10-09 · moteur `factorielle` · [donnees](../donnees/beta_vol.csv)_


### Rotation sectorielle

classement momentum 3 mois (10 secteurs) : 1. Energie (XLE) : +18.81% | 2. Technologie (XLK) : +6.78% | 3. Sante (XLV) : +6.13% | 4. Consommation de base (XLP) : -0.90% | 5. Finance (XLF) : -1.74%

_Statut **OK** · observation 2026-10-09 · moteur `factorielle` · [donnees](../donnees/rotation_sectorielle.csv) · [graphique](../graphiques/rotation_sectorielle/apercu.png)_


### Saisonnalite

rendement journalier moyen ete=+0.0180%, hiver=+0.0465% (t=-1.03, p=0.3048) -- non significatif (attendu vu la faible puissance sur seulement ~2 ans)

_Statut **OK** · observation 2026-10-09 · moteur `factorielle` · [donnees](../donnees/saisonnalite.csv)_


### Dispersion sectorielle

10 secteurs, rendement moyen 3m=+0.01%, dispersion (ecart-type)=7.97pt, etendue=27.69pt -- dispersion intermediaire

_Statut **OK** · observation 2026-10-09 · moteur `factorielle` · [donnees](../donnees/dispersion_sectorielle.csv)_


### Low volatility

tercile bas-vol ['XLF', 'XLRE', 'XLU'] Sharpe=-0.237 vs tercile haut-vol ['XLY', 'XLE', 'XLK'] Sharpe=0.324 -- anomalie low-vol non confirmee sur cet echantillon (puissance statistique faible, n petit -- limite assumee)

_Statut **OK** · observation 2026-10-09 · moteur `factorielle` · [donnees](../donnees/low_volatility.csv)_


### Momentum cross sectional

panier gagnant ['XLE', 'XLK', 'XLV'] (+10.57%) vs panier perdant ['XLRE', 'XLI', 'XLU'] (-7.51%) -- spread momentum=+18.09pt

_Statut **OK** · observation 2026-10-09 · moteur `factorielle` · [donnees](../donnees/momentum_cross_sectional.csv)_


### Cointegration secteurs

0/10 secteurs cointegres avec SP500 -- decouples : ['XLK', 'XLF', 'XLE', 'XLV', 'XLI', 'XLY', 'XLP', 'XLU', 'XLB', 'XLRE']  _(sans synthese)_

_Statut **OK** · observation 2026-10-09 · moteur `statistique` · [donnees](../donnees/cointegration_secteurs.csv)_


### Correlation facteurs

correlation entre momentum 3m et beta-VIX, 10 secteurs : +0.247 (facteurs largement independants)

_Statut **OK** · observation 2026-10-09 · moteur `factorielle` · [donnees](../donnees/correlation_facteurs.csv)_

