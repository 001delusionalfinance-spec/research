# Marches, facteurs et allocation

Change, actions, secteurs, facteurs, rotations et signaux d'allocation.

Mis a jour : **2026-09-25 07:53 UTC** · 16 lectures.

[Retour au tableau de bord](../README.md)

### Reer us

REER US=108.25 (rang percentile=94, variation YoY=+0.90%) -- dollar reel fort (competitivite reduite)

_Statut **OK** · observation 2026-07-01 · moteur `macro` · [donnees](../donnees/reer_us.csv) · [graphique](../graphiques/reer_us/apercu.png)_


### Differentiel taux change

8 paires testees sur variations a 21 jours -- le lien taux/change tient sur 8 paire(s) apres correction pour tests multiples : EURUSD, USDJPY, GBPUSD, USDCAD, AUDUSD, USDSEK, EURJPY, EURGBP

_Statut **OK** · observation 2026-09-17 · moteur `statistique` · [donnees](../donnees/differentiel_taux_change.csv) · [graphique](../graphiques/differentiel_taux_change/apercu.png)_


### Indices mondiaux

7 indices (devise locale) : Coree (KOSPI) +102.3% en tete sur 12 mois, Hong Kong (Hang Seng) -4.8% en queue -- ecart tres large entre blocs sur 12 mois (107pt) -- les cycles economiques ou les flux divergent nettement. ROTATION en cours : Coree (KOSPI) mene sur 12 mois mais Hong Kong (Hang Seng) a repris la tete sur 3 mois

_Statut **OK** · observation 2026-09-22 · moteur `factorielle` · [donnees](../donnees/indices_mondiaux.csv) · [graphique](../graphiques/indices_mondiaux/apercu.png)_


### Correlation glissante

correlation glissante 60j SP500/VIX = -0.781 (min=-0.955, max=-0.429 sur la fenetre d'historique disponible) -- proche de son minimum historique -- la relation SP500/VIX se renforce

_Statut **OK** · observation 2026-09-21 · moteur `statistique` · [donnees](../donnees/correlation_glissante.csv) · [graphique](../graphiques/correlation_glissante/apercu.png)_


### Clustering marches

32 marches, 4 clusters (average linkage, distance=1-|r|) : cluster 1 : ['EUR_FX', 'SP500_EMINI'] | cluster 2 : ['CORN', 'GBP_FX', 'NAT_GAS', 'PALLADIUM', 'SOFR_3M', 'SOYBEANS'] | cluster 3 : ['AUD_FX', 'BRENT_CRUDE', 'CAD_FX', 'CHF_FX', 'COPPER', 'GOLD', 'JPY_FX', 'MXN_FX', 'NASDAQ_MINI', 'NZD_FX', 'PLATINUM', 'RUSSELL_MINI', 'SILVER', 'USD_INDEX', 'UST_10Y', 'UST_2Y', 'UST_5Y', 'UST_BOND', 'UST_ULTRA_10Y', 'UST_ULTRA_BOND', 'VIX_FUT', 'WHEAT', 'WTI_CRUDE'] | cluster 4 : ['FED_FUNDS']

_Statut **OK** · observation 2026-09-15 · moteur `statistique` · [donnees](../donnees/clustering_marches.csv) · [graphique](../graphiques/clustering_marches/apercu.png)_


### Beta facteur macro

beta SP500/DGS10 (60j) = -0.0738 (rendement SP500 pour +1pt de taux 10 ans, 57/60 jours avec variation reelle) -- sensibilite elevee au facteur macro (choc de +100pb extrapole = -7.1%)

_Statut **OK** · observation 2026-09-18 · moteur `statistique` · [donnees](../donnees/beta_facteur_macro.csv) · [graphique](../graphiques/beta_facteur_macro/apercu.png)_


### Momentum prix

SP500 momentum 12-1 mois = 15.16% -- haussier (momentum positif), detail 1/3/6/12m = [1.18, 3.91, 17.99, 16.51]

_Statut **OK** · observation 2026-09-21 · moteur `factorielle` · [donnees](../donnees/momentum_prix.csv) · [graphique](../graphiques/momentum_prix/apercu.png)_


### Carry proxy

Chine : 1.54% vs US 3.88% -- diff=-2.34pt (carry negatif (taux < US))  _(sans synthese)_

_Statut **OK** · observation 2026-09-18 · moteur `factorielle` · [donnees](../donnees/carry_proxy.csv) · [graphique](../graphiques/carry_proxy/apercu.png)_


### Beta vol

beta SP500/VIX (60j) = -0.00492 (rendement SP500 pour +1pt VIX) -- sensibilite normale, relation inverse attendue (normale)

_Statut **OK** · observation 2026-09-21 · moteur `factorielle` · [donnees](../donnees/beta_vol.csv) · [graphique](../graphiques/beta_vol/apercu.png)_


### Rotation sectorielle

classement momentum 3 mois (10 secteurs) : 1. Energie (XLE) : +15.54% | 2. Sante (XLV) : +12.63% | 3. Finance (XLF) : +4.10% | 4. Technologie (XLK) : +1.41% | 5. Consommation de base (XLP) : -0.32%

_Statut **OK** · observation 2026-09-21 · moteur `factorielle` · [donnees](../donnees/rotation_sectorielle.csv) · [graphique](../graphiques/rotation_sectorielle/apercu.png)_


### Saisonnalite

rendement journalier moyen ete=+0.0183%, hiver=+0.0465% (t=-1.02, p=0.3091) -- non significatif (attendu vu la faible puissance sur seulement ~2 ans)

_Statut **OK** · observation 2026-09-21 · moteur `factorielle` · [donnees](../donnees/saisonnalite.csv) · [graphique](../graphiques/saisonnalite/apercu.png)_


### Dispersion sectorielle

10 secteurs, rendement moyen 3m=+0.85%, dispersion (ecart-type)=7.53pt, etendue=24.62pt -- dispersion intermediaire

_Statut **OK** · observation 2026-09-21 · moteur `factorielle` · [donnees](../donnees/dispersion_sectorielle.csv) · [graphique](../graphiques/dispersion_sectorielle/apercu.png)_


### Low volatility

tercile bas-vol ['XLF', 'XLRE', 'XLU'] Sharpe=-0.352 vs tercile haut-vol ['XLY', 'XLE', 'XLK'] Sharpe=0.404 -- anomalie low-vol non confirmee sur cet echantillon (puissance statistique faible, n petit -- limite assumee)

_Statut **OK** · observation 2026-09-21 · moteur `factorielle` · [donnees](../donnees/low_volatility.csv) · [graphique](../graphiques/low_volatility/apercu.png)_


### Momentum cross sectional

panier gagnant ['XLE', 'XLV', 'XLF'] (+10.75%) vs panier perdant ['XLB', 'XLI', 'XLU'] (-6.43%) -- spread momentum=+17.18pt

_Statut **OK** · observation 2026-09-21 · moteur `factorielle` · [donnees](../donnees/momentum_cross_sectional.csv) · [graphique](../graphiques/momentum_cross_sectional/apercu.png)_


### Cointegration secteurs

0/10 secteurs cointegres avec SP500 -- decouples : ['XLK', 'XLF', 'XLE', 'XLV', 'XLI', 'XLY', 'XLP', 'XLU', 'XLB', 'XLRE']  _(sans synthese)_

_Statut **OK** · observation 2026-09-21 · moteur `statistique` · [donnees](../donnees/cointegration_secteurs.csv) · [graphique](../graphiques/cointegration_secteurs/apercu.png)_


### Correlation facteurs

correlation entre momentum 3m et beta-VIX, 10 secteurs : +0.352 (facteurs largement independants)

_Statut **OK** · observation 2026-09-21 · moteur `factorielle` · [donnees](../donnees/correlation_facteurs.csv) · [graphique](../graphiques/correlation_facteurs/apercu.png)_

