# Taux, credit et liquidite

Courbes souveraines, conditions financieres, credit, emission et taux reels.

Mis a jour : **2026-09-27 21:44 UTC** · 13 lectures.

[Retour au tableau de bord](../README.md)

### Taux reel us

nominal=3.88%, inflation YoY=3.35%, reel=0.53% -- restrictif (taux reel positif et eleve)

_Statut **OK** · observation 2026-09-24 · moteur `macro` · [donnees](../donnees/taux_reel_us.csv) · [graphique](../graphiques/taux_reel_us/apercu.png)_


### Courbe taux us

10 ans=5.18%, 2 ans=4.87%, spread=+0.31pt -- normale (0 run(s) consecutif(s) dans l'historique accumule)

_Statut **OK** · observation 2026-09-24 · moteur `macro` · [donnees](../donnees/courbe_taux_us.csv) · [graphique](../graphiques/courbe_taux_us/apercu.png)_


### Cycle credit

credit bancaire total croissance YoY=+6.15%, rang percentile historique=39.7196261682243, lecture=normal

_Statut **OK** · observation 2026-09-16 · moteur `macro` · [donnees](../donnees/cycle_credit.csv)_


### Conditions financieres

indice conditions financieres=+0.064 (3 composantes: {'taux_directeur': 0.5985724560125544, 'courbe_inversee': 0.2531563730537784, 'vix': -0.6597998970697634}) -- conditions proches de la normale

_Statut **OK** · observation 2026-09-24 · moteur `macro` · [donnees](../donnees/conditions_financieres.csv) · [graphique](../graphiques/conditions_financieres/apercu.png)_


### Emission tresor us

84 derniers jours, 7886 Mds$ offerts : court (moins d'un an) 6798 Mds$ (86%), intermediaire (2 a 10 ans) 969 Mds$ (12%), long (20 a 30 ans) 119 Mds$ (2%) -- financement concentre sur le court et l'intermediaire, part longue a 2% -- peu de pression par la duration

_Statut **OK** · observation non exposee par la sortie · moteur `macro` · [donnees](../donnees/emission_tresor_us.csv)_


### Pentes courbes

7 courbes : pente de +0.30pt (Australie) a +1.20pt (Japon) -- aucune courbe inversee -- pas de signal recessif par la pente

_Statut **OK** · observation 2026-09-25 · moteur `series-temporelles` · [donnees](../donnees/pentes_courbes.csv) · [graphique](../graphiques/pentes_courbes/apercu.png)_


### Stationnarite taux

1/5 series stationnaires (niveau, pas en difference) -- a garder en tete avant toute correlation/regression sur ces series telles quelles  _(sans synthese)_

_Statut **OK** · observation 2026-09-24 · moteur `statistique` · [donnees](../donnees/stationnarite_taux.csv)_


### Cointegration taux

1/10 paires cointegrees  _(sans synthese)_

_Statut **OK** · observation 2026-09-24 · moteur `statistique` · [donnees](../donnees/cointegration_taux.csv)_


### Pca taux

61 dates communes -- PC1 explique 94.7% de la variance conjointe (vs 20% attendu si les 5 blocs etaient independants) -- synchronisation forte -- un facteur commun domine largement le mouvement conjoint, poids PC1={'Chine': -0.095, 'Japon': 0.035, 'Royaume-Uni': 0.616, 'US': 0.592, 'Zone_euro': 0.51}

_Statut **OK** · observation 2026-07-01 · moteur `statistique` · [donnees](../donnees/pca_taux.csv)_


### Hp filter taux

taux 10 ans observe=5.180%, tendance HP=4.960%, ecart cyclique=+0.220pt -- au-dessus de sa tendance locale

_Statut **OK** · observation 2026-09-24 · moteur `series-temporelles` · [donnees](../donnees/hp_filter_taux.csv) · [graphique](../graphiques/hp_filter_taux/apercu.png)_


### Facteur qualite credit

spread HY=2.80, IG=0.79, ecart=2.01pt (niveau contenu), variation 6m=-13.7% -- se resserre (risque credit percu en baisse)

_Statut **OK** · observation 2026-09-24 · moteur `factorielle` · [donnees](../donnees/facteur_qualite_credit.csv) · [graphique](../graphiques/facteur_qualite_credit/apercu.png)_


### Ornstein uhlenbeck credit

spread HY actuel=2.80, niveau moyen estime=3.02, demi-vie=41.9j, ecart actuel=-0.22 -- spread HY actuel en-dessous de son niveau moyen de long terme

_Statut **OK** · observation 2026-09-24 · moteur `series-temporelles` · [donnees](../donnees/ornstein_uhlenbeck_credit.csv)_


### Momentum credit

momentum credit 12-1 mois=+0.00pt -- stable

_Statut **OK** · observation 2026-09-24 · moteur `factorielle` · [donnees](../donnees/momentum_credit.csv)_

