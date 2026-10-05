# Taux, credit et liquidite

Courbes souveraines, conditions financieres, credit, emission et taux reels.

Mis a jour : **2026-10-05 04:24 UTC** · 13 lectures.

[Retour au tableau de bord](../README.md)

### Taux reel us

nominal=3.88%, inflation YoY=3.35%, reel=0.53% -- restrictif (taux reel positif et eleve)

_Statut **OK** · observation 2026-10-01 · moteur `macro` · [donnees](../donnees/taux_reel_us.csv) · [graphique](../graphiques/taux_reel_us/apercu.png)_


### Courbe taux us

10 ans=5.24%, 2 ans=4.78%, spread=+0.46pt -- normale (0 run(s) consecutif(s) dans l'historique accumule)

_Statut **OK** · observation 2026-10-01 · moteur `macro` · [donnees](../donnees/courbe_taux_us.csv) · [graphique](../graphiques/courbe_taux_us/apercu.png)_


### Cycle credit

credit bancaire total croissance YoY=+6.02%, rang percentile historique=38.006230529595015, lecture=normal

_Statut **OK** · observation 2026-09-23 · moteur `macro` · [donnees](../donnees/cycle_credit.csv)_


### Conditions financieres

indice conditions financieres=-0.002 (3 composantes: {'taux_directeur': 0.5960734758921187, 'courbe_inversee': 0.003384125958412214, 'vix': -0.6053288580101447}) -- conditions proches de la normale

_Statut **OK** · observation 2026-10-01 · moteur `macro` · [donnees](../donnees/conditions_financieres.csv) · [graphique](../graphiques/conditions_financieres/apercu.png)_


### Emission tresor us

84 derniers jours, 7848 Mds$ offerts : court (moins d'un an) 6760 Mds$ (86%), intermediaire (2 a 10 ans) 969 Mds$ (12%), long (20 a 30 ans) 119 Mds$ (2%) -- financement concentre sur le court et l'intermediaire, part longue a 2% -- peu de pression par la duration

_Statut **OK** · observation non exposee par la sortie · moteur `macro` · [donnees](../donnees/emission_tresor_us.csv)_


### Pentes courbes

7 courbes : pente de +0.40pt (Australie) a +1.10pt (Japon) -- aucune courbe inversee -- pas de signal recessif par la pente

_Statut **OK** · observation 2026-10-02 · moteur `series-temporelles` · [donnees](../donnees/pentes_courbes.csv) · [graphique](../graphiques/pentes_courbes/apercu.png)_


### Stationnarite taux

1/5 series stationnaires (niveau, pas en difference) -- a garder en tete avant toute correlation/regression sur ces series telles quelles  _(sans synthese)_

_Statut **OK** · observation 2026-10-01 · moteur `statistique` · [donnees](../donnees/stationnarite_taux.csv)_


### Cointegration taux

1/10 paires cointegrees  _(sans synthese)_

_Statut **OK** · observation 2026-10-01 · moteur `statistique` · [donnees](../donnees/cointegration_taux.csv)_


### Pca taux

61 dates communes -- PC1 explique 94.7% de la variance conjointe (vs 20% attendu si les 5 blocs etaient independants) -- synchronisation forte -- un facteur commun domine largement le mouvement conjoint, poids PC1={'Chine': -0.095, 'Japon': 0.035, 'Royaume-Uni': 0.616, 'US': 0.592, 'Zone_euro': 0.51}

_Statut **OK** · observation 2026-07-01 · moteur `statistique` · [donnees](../donnees/pca_taux.csv)_


### Hp filter taux

taux 10 ans observe=5.240%, tendance HP=5.090%, ecart cyclique=+0.150pt -- au-dessus de sa tendance locale

_Statut **OK** · observation 2026-10-01 · moteur `series-temporelles` · [donnees](../donnees/hp_filter_taux.csv) · [graphique](../graphiques/hp_filter_taux/apercu.png)_


### Facteur qualite credit

spread HY=3.24, IG=0.86, ecart=2.38pt (niveau contenu), variation 6m=+3.0% -- s'ecarte (risque credit percu en hausse)

_Statut **OK** · observation 2026-10-01 · moteur `factorielle` · [donnees](../donnees/facteur_qualite_credit.csv) · [graphique](../graphiques/facteur_qualite_credit/apercu.png)_


### Ornstein uhlenbeck credit

spread HY actuel=3.24, niveau moyen estime=3.04, demi-vie=35.8j, ecart actuel=+0.20 -- spread HY actuel au-dessus de son niveau moyen de long terme

_Statut **OK** · observation 2026-10-01 · moteur `series-temporelles` · [donnees](../donnees/ornstein_uhlenbeck_credit.csv)_


### Momentum credit

momentum credit 12-1 mois=-0.16pt -- spread qui se resserre (risque credit percu en baisse)

_Statut **OK** · observation 2026-10-01 · moteur `factorielle` · [donnees](../donnees/momentum_credit.csv)_

