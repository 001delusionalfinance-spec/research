# Lecture du jour -- 2026-09-16 11:56 UTC

111 modeles sur 111 ont produit une lecture.

> 12 modele(s) n'ont **pas de ligne de synthese** : ils enumerent sans conclure. La lecture affichee pour eux est un repli sur leur derniere ligne, elle est signalee par _(sans synthese)_ et ne resume pas l'ensemble de leur sortie.

## factorielle

- **indices_mondiaux** -- 7 indices (devise locale) : Coree (KOSPI) +96.9% en tete sur 12 mois, Hong Kong (Hang Seng) -5.6% en queue -- ecart tres large entre blocs sur 12 mois (102pt) -- les cycles economiques ou les flux divergent nettement. ROTATION en cours : Coree (KOSPI) mene sur 12 mois mais Royaume-Uni (FTSE 100) a repris la tete sur 3 mois
- **momentum_prix** -- SP500 momentum 12-1 mois = 17.69% -- haussier (momentum positif), detail 1/3/6/12m = [-2.57, 0.99, 12.95, 14.67]
- **carry_proxy** -- Chine : 1.54% vs US 3.63% -- diff=-2.09pt (carry negatif (taux < US))  _(sans synthese)_
- **beta_vol** -- beta SP500/VIX (60j) = -0.00499 (rendement SP500 pour +1pt VIX) -- sensibilite normale, relation inverse attendue (normale)
- **rotation_sectorielle** -- classement momentum 3 mois (10 secteurs) : 1. Energie (XLE) : +19.09% | 2. Sante (XLV) : +9.62% | 3. Finance (XLF) : +4.60% | 4. Technologie (XLK) : -1.45% | 5. Consommation de base (XLP) : -2.17%
- **saisonnalite** -- rendement journalier moyen ete=+0.0177%, hiver=+0.0465% (t=-1.04, p=0.3002) -- non significatif (attendu vu la faible puissance sur seulement ~2 ans)
- **dispersion_sectorielle** -- 10 secteurs, rendement moyen 3m=+0.06%, dispersion (ecart-type)=8.17pt, etendue=27.39pt -- dispersion intermediaire
- **low_volatility** -- tercile bas-vol ['XLF', 'XLRE', 'XLU'] Sharpe=-0.187 vs tercile haut-vol ['XLY', 'XLE', 'XLK'] Sharpe=0.475 -- anomalie low-vol non confirmee sur cet echantillon (puissance statistique faible, n petit -- limite assumee)
- **facteur_qualite_credit** -- spread HY=2.71, IG=0.80, ecart=1.91pt (niveau contenu), variation 6m=-18.0% -- se resserre (risque credit percu en baisse)
- **momentum_cross_sectional** -- panier gagnant ['XLE', 'XLV', 'XLF'] (+11.11%) vs panier perdant ['XLI', 'XLY', 'XLU'] (-6.94%) -- spread momentum=+18.04pt
- **qualite_regime_macro** -- instabilite taux=0.0000, instabilite VIX=0.0643 -- score qualite du regime=-0.0322 (plus haut = regime plus stable/previsible)
- **momentum_credit** -- momentum credit 12-1 mois=-0.12pt -- spread qui se resserre (risque credit percu en baisse)
- **correlation_facteurs** -- correlation entre momentum 3m et beta-VIX, 10 secteurs : +0.478 (facteurs lies (diversification reduite))

## macro

- **regime_monetaire_emploi** -- Chine : taux 1.54% (stable, niveau bas) -- chomage non_couvert  _(sans synthese)_
- **sahm_rule** -- MM3 chomage=4.13%, plus bas 12m=4.13%, ecart=0.00pt (seuil 0.5pt) -- non declenchee
- **taux_reel_us** -- nominal=3.63%, inflation YoY=3.35%, reel=0.28% -- accommodant (taux reel negatif ou proche de zero)
- **regle_taylor** -- Taylor (2 termes, sans output gap)=6.03%, Fed reel=3.63%, ecart=-2.40pt -- accommodant (Fed en-dessous de la regle)
- **courbe_taux_us** -- 10 ans=4.97%, 2 ans=4.65%, spread=+0.32pt -- normale (0 run(s) consecutif(s) dans l'historique accumule)
- **cycle_credit** -- credit bancaire total croissance YoY=+5.99%, rang percentile historique=38.161993769470406, lecture=normal
- **conditions_financieres** -- indice conditions financieres=+0.114 (3 composantes: {'taux_directeur': 0.4729218721337119, 'courbe_inversee': 0.24096018025245844, 'vix': -0.37175642697219097}) -- conditions proches de la normale
- **reer_us** -- REER US=108.25 (rang percentile=94, variation YoY=+0.90%) -- dollar reel fort (competitivite reduite)
- **cycle_immobilier** -- mises en chantier=1239.0k (baisse), permis=1433.0k (baisse), taux hypothecaire=6.76% -- pas de divergence
- **inflation_comparee** -- inflation annuelle sur 12 blocs : mediane 2.88%, dispersion 3.88pt (Nouvelle-Zelande +4.06% au plus haut, Suede +0.18% au plus bas) -- dispersion forte -- les banques centrales sont poussees a diverger, ce qui deplace les differentiels de taux et le change
- **divergence_taux_directeurs** -- 12 banques centrales : ecart de taux max 4.35pt (Australie 4.35% contre Suisse 0.00%), mediane 2.88% -- cycles alignes dans le meme sens (resserrement) -- divergence limitee
- **bilans_banques_centrales** -- 9 bilans suivis sur 12 mois : de -14.4% (RBA -- titres locaux) a +8.4% (Fed -- titres du Tresor) -- regimes OPPOSES -- 5 bilan(s) en reduction pendant que 4 s'etendent, la liquidite mondiale ne va pas dans un sens unique
- **liquidite_nette_fed** -- liquidite nette 5.51 T$ au 2026-09-09 (-1.3% sur 3 mois, -2.3% sur 12 mois) -- liquidite en retrait sur 3 mois -- conditions de financement qui se durcissent. Detail : actif 6.74 T$, compte du Tresor 0.88 T$, reverse repo 0.35 T$
- **activite_zone_euro** -- zone euro : Production industrielle -0.2 % sur 12 mois, Ventes de detail +0.8 % sur 12 mois, Taux de chomage +0.1 pt sur 12 mois, Confiance industrielle +1.2 pt vs moyenne longue -- production industrielle DIVERGENTE entre grands pays -- en hausse : Espagne ; en baisse : Allemagne, France, Italie
- **soutenabilite_dette** -- 8 pays. charge la plus lourde : Canada a 25.5% du revenu. taux 10 ans AU-DESSUS de l'inflation dans 5 pays -- Royaume-Uni (+2.6pt), Etats-Unis (+1.6pt), Zone euro (+1.1pt), Japon (+1.0pt), Canada (+0.9pt). Configuration ou le ratio d'endettement monte meme a budget primaire equilibre (approximation : croissance nominale reduite a l'inflation)
- **matieres_premieres_macro** -- ratio cuivre/or stable -- pas de signal net sur la croissance (+0.1% sur 3 mois). Brent 108.3$ (+37.2% sur 3 mois, +60.6% sur 12 mois), gaz -9.1% sur 3 mois, ecart Brent-WTI +3.0$ -- energie nettement plus chere sur un an -- pression inflationniste a venir que les prix a la consommation ne montrent pas encore
- **emission_tresor_us** -- 84 derniers jours, 7715 Mds$ offerts : court (moins d'un an) 6696 Mds$ (87%), intermediaire (2 a 10 ans) 900 Mds$ (12%), long (20 a 30 ans) 119 Mds$ (2%) -- financement concentre sur le court et l'intermediaire, part longue a 2% -- peu de pression par la duration
- **surprise_macro_composite** -- indice de surprise macro=-0.33 ({'chomage': 1, 'credit_bancaire': -1, 'inflation': -1}) -- negatif (surprises defavorables dominent)
- **balance_commerciale** -- balance commerciale=-88,576M$ (rang percentile=1), deficit se creuse
- **surprise_inflation** -- CPI MoM=+0.396%, prevision naive=+0.316%, surprise=+0.080pt -- surprise haussiere (inflation plus forte qu'attendu)

## ml

- **walkforward_direction** -- 7516 predictions walk-forward -- momentum 5j=0.4963 vs baseline majoritaire=0.5378 -- NE BAT PAS la baseline (resultat honnete, pas ajuste pour paraitre mieux)
- **anomalie_multivariee** -- distance de Mahalanobis=1.010 (seuil 3.0) -- jour ordinaire
- **test_overfitting** -- meilleure fenetre in-sample=23j (accuracy=0.5165) vs meme fenetre en walk-forward=0.5168 -- ecart=-0.0002 (ecart faible)
- **prevision_vol_regression** -- regression AR(1) (a=0.000116, b=0.2096) MSE=2.9849e-07 vs baseline persistance MSE=3.8338e-07 -- BAT la baseline (resultat honnete, pas ajuste)
- **kmeans_regimes** -- 2047 points, k=3 -- point actuel (VIX=17.1, spread=+0.32, taux=3.63%) -> cluster 1 (tailles : {0: 514, 1: 932, 2: 601}) -- regime calme (VIX du cluster en-dessous de la moyenne historique)
- **ensemble_signaux** -- 7516 predictions -- momentum=0.4963, vix=0.4985, ensemble=0.4985, baseline=0.5378 -- ensemble NE BAT PAS la baseline
- **screening_features** -- 2/4 features avec un lien univarie significatif (p<0.05, sans correction multiple-testing ici -- seulement 4 tests)  _(sans synthese)_
- **couts_transaction** -- 7516 predictions, 1510 changements de position (5pb/changement) -- rendement cumule brut=-92.81%, cout total=53.01%, net=-96.62% -- les frais mangent une part importante du rendement (>50% du brut)
- **regression_multifeatures** -- coefs (intercept=0.00029, momentum5j=-0.0326, var_vix=0.00027) -- R2 out-of-sample=0.0102 (modele bat la moyenne)
- **stacking** -- poids appris (momentum=-0.079, baseline=0.089, biais=0.089) -- accuracy stacking=0.5477 vs momentum seul=0.5029, baseline seule=0.5477 sur 2255 points test -- stacking NE BAT PAS la baseline, meilleur=stacking / baseline (ex-aequo)
- **decision_stump** -- seuil appris=-1.530 (sens=False) -- accuracy stump=0.5473 vs baseline=0.5486 sur 2264 points test -- stump NE BAT PAS la baseline
- **importance_permutation** -- R2 base=0.0102 -- importance momentum5j=0.00245, importance variation_vix=0.01030 -- VIX plus important

## nlp

- **ton_banques_centrales** -- variation du ton depuis la publication precedente, par institution (pour mille, meme lexique) : Fed -4.28, BCE +12.50, Banque d'Angleterre -4.90 -- les tons DIVERGENT -- BCE se detend pendant que Fed, Banque d'Angleterre se durcit. Les niveaux ne sont PAS comparables entre institutions : un seul mot de ton les deplace de Fed 6.7, BCE 0.6, Banque d'Angleterre 0.3 pour mille respectivement, selon la longueur du document
- **ton_fomc** -- 20260617 -> 20260729 : ton +17.70‰ -> +13.42‰ (diff -4.28‰, ton qui se degrade), taux inchange (3-1/2 to 3-3/4), dissidents 0 -> 3
- **frequence_mots_cles_fomc** -- communique 20260729, 151 mots -- mots-cles presents : {'uncertainty': 1, 'elevated': 2, 'solid': 1, 'strong': 1} -- theme dominant : 'elevated' (2 mention(s))
- **complexite_texte_fomc** -- communique 20260729 : 149 mots, 10 phrases (14.9 mots/phrase en moyenne, phrases de longueur moderee), 32.9% de mots longs (>6 lettres, vocabulaire dense)
- **ton_minutes_fomc** -- 20260617 -> 20260729 : ton +2.49pm -> +3.97pm (diff +1.49pm, ton qui s'ameliore), 4780 mots (67 positifs, 48 negatifs)
- **ecart_communique_minutes** -- reunion 20260729 : communique=+13.42pm, minutes=+3.97pm -- ecart=+9.45pm (communique plus positif)
- **complexite_texte_minutes** -- minutes 20260729 : 4780 mots, 231 phrases (20.7 mots/phrase, phrases longues), 35.6% de mots longs (>6 lettres, vocabulaire dense)
- **entites_geographiques_minutes** -- minutes 20260729 -- mentions : {'Middle East': 12, 'labor_market': 22, 'inflation': 51, 'tariffs': 7, 'housing': 3} -- focus dominant : 'inflation' (51 mention(s))
- **similarite_vocabulaire_minutes** -- 20260617 -> 20260729 : Jaccard=0.5209 (vocabulaire moderement renouvele) (648 mots communs / 1244 mots uniques au total), 368 nouveaux, 228 disparus
- **lisibilite_flesch_kincaid** -- communique (20260729) : Reading Ease=48.6 (0=tres difficile, 100=tres facile), Grade Level=10.2
- **frequence_mots_cles_minutes** -- minutes 20260729, 4717 mots -- mots-cles : {'uncertainty': 8, 'uncertain': 1, 'risks': 6, 'elevated': 17, 'solid': 12, 'strong': 13, 'resilient': 3, 'restrictive': 7} -- theme dominant : 'elevated' (17 mention(s))
- **langage_prudence** -- minutes 20260729 : 74 mots de prudence sur 4780 (15.48 pour mille, langage prudent)
- **intensite_desaccord** -- minutes 20260729 : 3 dissident(s) au vote, 20 mention(s) de desaccord dans le texte ({'disagreed': 0, 'preferred': 1, 'dissent': 0, 'alternative view': 0, 'some participants': 11, 'a few participants': 6, 'several participants noted': 2}) -- desaccord notable

## positionnement-comportemental

- **positionnement_courbe_taux** -- 8 contrats de taux -- pari de NIVEAU -- courtes et longues sont short, le marche joue un deplacement de toute la courbe dans le meme sens. Positionnement a un extreme historique sur : SOFR 3 mois (extreme bas, 0e pct), Bond (30 ans) (extreme bas, 3e pct)
- **positionnement_devises** -- 8 devises (net positif = pari haussier sur la devise etrangere, jamais sur le dollar) -- aucune position de carry identifiee. A un extreme historique : Dollar neo-zelandais (extreme haut, 92e pct), Livre sterling (extreme bas, 13e pct), Franc suisse (extreme bas, 11e pct), Dollar canadien (extreme bas, 10e pct) -- un positionnement extreme est vulnerable a un deboucle rapide si la volatilite monte
- **positionnement_cot** -- WTI_CRUDE : net=136579.0, z=0.05, extreme=False  _(sans synthese)_
- **momentum_positionnement** -- WTI_CRUDE : z=+0.05 (il y a 8sem: -1.36), momentum=+1.41 -- positionnement se degonfle (l'extreme diminue)  _(sans synthese)_
- **crowding_cross_asset** -- 15/32 marches avec |z|>=1.5 simultanement : BRENT_CRUDE(-1.61);COPPER(+2.24);CORN(+2.56);EUR_FX(-1.86);NAT_GAS(-1.87);NZD_FX(+2.08);RUSSELL_MINI(-1.83);SOFR_3M(-2.39);SOYBEANS(+1.76);USD_INDEX(+1.84);UST_2Y(+2.06);UST_5Y(+1.56);UST_BOND(-1.79);UST_ULTRA_BOND(-1.90);WHEAT(+1.93)
- **divergence_cot_prix** -- SP500 -2.57% sur 30j, COT net -27258 -> -76036 -- pas de divergence
- **ratio_commercial_speculatif** -- WTI_CRUDE : commercial=-166185, speculatif=+136579, ratio=1.22, sens_oppose=True  _(sans synthese)_
- **rotation_risk_on_off** -- z-score moyen risque=+0.34 ({'SP500_EMINI': 0.6293714609899971, 'NASDAQ_MINI': 0.045621243567282935}), refuge=+0.41 ({'GOLD': 0.9541575293930288, 'UST_10Y': -0.14271422703766087}) -- posture=mixte/neutre
- **concentration_traders** -- WTI_CRUDE : 299 traders, position nette moyenne/trader=457 -- diffus (large base de traders) (mediane du groupe : 459)  _(sans synthese)_
- **metaux_precieux** -- z-scores : {'GOLD': 0.9541575293930288, 'SILVER': -0.8114797378614697, 'PLATINUM': -0.1233387190408433} -- GOLD le plus tendu, sans franchir le seuil extreme (|z|>2) -- ecart or/industriels=+1.42
- **persistance_extremes** -- 32 marches analyses, plus longue persistance : SOFR_3M (19 semaines)
- **dollar_smile** -- USD_INDEX net=+17604 (long), 2/3 devises non-USD nettes courtes -- positionnement coherent
- **extremes_historiques** -- 32 marches -- le plus proche de son record directionnel : COPPER (100% de son record)
- **correlation_cot_prix** -- correlation COT/prix SP500 (26 semaines) = +0.060 -- lien faible

## risque

- **vol_cross_asset** -- 6 mesures de volatilite : Petrole (OVX) 92e pct, Or (GVZ) 92e pct, Vol de la vol (VVIX) 49e pct, Nasdaq (VXN) 49e pct, Actions US (VIX) 45e pct, Taux US (MOVE) 29e pct -- stress LOCALISE sur Petrole (OVX), Or (GVZ) pendant que le reste ne l'est pas -- episode propre a cette classe d'actifs, pas une aversion au risque d'ensemble
- **var_drawdown** -- VaR95=-1.45% CVaR95=-1.80% VaR99=-2.08% CVaR99=-2.50% drawdown_max_252j=-9.10% -- soit l'equivalent de ~6 jours de VaR95 d'affilee
- **skew_kurtosis** -- skewness=-0.215 (asymetrie negative (pertes extremes > gains extremes)), kurtosis exces=+1.126 (queues epaisses (risque extreme sous-estime par une hypothese normale))
- **ratios_performance** -- Sharpe=1.068 (bon), Sortino=1.044 (bon), Calmar=1.511 (bon) -- lecture sur fenetre 252j (~1 an, echantillon limite), seuils academiques standards, taux sans risque suppose nul
- **covar** -- VaR95 inconditionnelle=-1.84%, VaR95|VIX detresse(>=29.5)=-4.37%, VaR95|VIX normal=-1.52% -- DeltaCoVaR=-2.86pt (755 jours de detresse dans l'echantillon) -- contagion notable -- VaR 2.9x plus severe en detresse
- **stress_test_historique** -- COVID_2020 (2020-02-19 -> 2020-03-23) : chute historique=-33.9% -- rejouee sur le niveau actuel (7586) -> 5012  _(sans synthese)_
- **sizing_robuste** -- vol point estimate=0.1285, IC90%=[0.1160, 0.1405] (1000 tirages bootstrap) -- intervalle etroit (19% du point estimate) -- estimation relativement fiable
- **nombre_effectif_paris** -- 32 marches, nombre effectif de paris independants=13.39 (42% du maximum theorique de 32) -- moderement concentre -- redondance significative entre plusieurs paris
- **detection_saut** -- Z-stat BNS (fenetre 22j)=-0.903 (seuil ±1.96) -- pas de saut isole detecte
- **choc_taux** -- beta SP500/DGS10=-0.0646 -- choc +100pb : -6.46% (SP500 7620 -> 7128) ; choc -100pb : +6.46% (-> 8112)
- **var_conditionnelle_regime** -- regime VIX actuel=bas (rang percentile=32) -- VaR95 applicable maintenant=-1.14% (vs VaR95 globale non-conditionnelle=-1.84%)
- **ratios_conditionnels_regime** -- Sharpe regime haut-vol=-1.107, bas-vol=2.400, global=0.420 -- meilleur en regime calme, comme attendu
- **choc_vol_parametrique** -- vol actuelle=12.85%, scenarios x1/x2/x3 calcules -- pire scenario (x3) = -3.94%/jour, soit 3.1x le scenario de base

## series-temporelles

- **pentes_courbes** -- 7 courbes : pente de +0.32pt (Etats-Unis) a +1.20pt (Japon) -- aucune courbe inversee -- pas de signal recessif par la pente
- **volatilite_ewma** -- vol realisee 60j=0.11136035451137334, EWMA=0.1022 (tendance 10 runs: indisponible (moins de 11 runs accumules -- tendance pas encore mesurable))
- **garch** -- vol GARCH(1,1) annualisee=0.1133 (alpha=0.114, beta=0.869, persistance=0.983 -- tres proche de 1 -- chocs de volatilite tres durables)
- **hurst** -- Hurst=0.5491 (R2 regression=0.999) -- proche de la marche aleatoire (H~0.5)
- **ornstein_uhlenbeck_vix** -- VIX actuel=17.20, niveau moyen estime (mu)=20.22, demi-vie=28.8j, ecart actuel=-3.02 -- VIX actuel en-dessous de son niveau moyen de long terme
- **changepoint_volatilite** -- rupture detectee le 2011-12-21 -- vol avant=0.2127, vol apres=0.1667 (reduction SSE=0.5%) -- baisse de la vol au point de rupture (-21.6%)
- **kalman_niveau_local** -- VIX observe=17.20, filtre Kalman=17.16 (ecart-type=0.62), ratio signal/bruit=0.2052 -- le filtre lisse fortement le bruit, reagit lentement (ecart obs.-filtre=+0.04)
- **hp_filter_taux** -- taux 10 ans observe=4.970%, tendance HP=4.823%, ecart cyclique=+0.147pt -- au-dessus de sa tendance locale
- **var_sp500_vix** -- VAR ordre choisi par AIC=10 -- coef SP500(t-1)->VIX(t)=0.4229140080726541 (SP500(t-1) en hausse -> VIX(t) tend aussi a monter), coef VIX(t-1)->SP500(t)=-0.05236794819901587 (VIX(t-1) en hausse -> SP500(t) tend a baisser)
- **analyse_spectrale** -- 3 periodes dominantes (jours de bourse) : [2.2, 4.0, 5.4] -- cycle(s) connu(s) qui ressortent : 4.0j~hebdomadaire, 5.4j~hebdomadaire
- **arima** -- ARIMA(1,1,1) sur 100 previsions 1-jour test : RMSE=2.332 vs baseline naive MSE=5.500 -- ARIMA bat la persistance simple
- **decomposition_stl** -- VIX : tendance=16.01, composante saisonniere (periode 5j)=+0.667, residu=+0.522 -- la saisonnalite explique 0.71% de la variance totale (negligeable)
- **ornstein_uhlenbeck_credit** -- spread HY actuel=2.71, niveau moyen estime=3.02, demi-vie=47.0j, ecart actuel=-0.31 -- spread HY actuel en-dessous de son niveau moyen de long terme

## statistique

- **differentiel_taux_change** -- 8 paires testees sur variations a 21 jours -- le lien taux/change tient sur 6 paire(s) apres correction pour tests multiples : EURUSD, USDJPY, USDCAD, USDSEK, EURJPY, EURGBP
- **correlations_positionnement** -- 260/496 paires significatives apres correction Bonferroni (alpha=0.05/496)  _(sans synthese)_
- **stationnarite_taux** -- 1/5 series stationnaires (niveau, pas en difference) -- a garder en tete avant toute correlation/regression sur ces series telles quelles  _(sans synthese)_
- **correlation_glissante** -- correlation glissante 60j SP500/VIX = -0.792 (min=-0.955, max=-0.429 sur la fenetre d'historique disponible) -- proche de son minimum historique -- la relation SP500/VIX se renforce
- **cointegration_taux** -- 1/10 paires cointegrees  _(sans synthese)_
- **pca_taux** -- 61 dates communes -- PC1 explique 94.7% de la variance conjointe (vs 20% attendu si les 5 blocs etaient independants) -- synchronisation forte -- un facteur commun domine largement le mouvement conjoint, poids PC1={'Chine': -0.095, 'Japon': 0.035, 'Royaume-Uni': 0.616, 'US': 0.592, 'Zone_euro': 0.51}
- **clustering_marches** -- 32 marches, 4 clusters (average linkage, distance=1-|r|) : cluster 1 : ['EUR_FX', 'SP500_EMINI'] | cluster 2 : ['CORN', 'GBP_FX', 'NAT_GAS', 'PALLADIUM', 'SOFR_3M', 'SOYBEANS'] | cluster 3 : ['AUD_FX', 'BRENT_CRUDE', 'CAD_FX', 'CHF_FX', 'COPPER', 'GOLD', 'JPY_FX', 'MXN_FX', 'NASDAQ_MINI', 'NZD_FX', 'PLATINUM', 'RUSSELL_MINI', 'SILVER', 'USD_INDEX', 'UST_10Y', 'UST_2Y', 'UST_5Y', 'UST_BOND', 'UST_ULTRA_10Y', 'UST_ULTRA_BOND', 'VIX_FUT', 'WHEAT', 'WTI_CRUDE'] | cluster 4 : ['FED_FUNDS']
- **causalite_granger** -- causalite Granger detectee : SP500_cause_VIX (lag=5)
- **dependance_queue** -- 518/7546 jours conjointement extremes (SP500 pire 10% ET VIX pire 10%), P observee=0.0686 vs P sous independance=0.0100 -- coefficient de dependance de queue=6.86 (dependance reelle)
- **beta_facteur_macro** -- beta SP500/DGS10 (60j) = -0.0646 (rendement SP500 pour +1pt de taux 10 ans, 57/60 jours avec variation reelle) -- sensibilite elevee au facteur macro (choc de +100pb extrapole = -6.3%)
- **decomposition_variance** -- R² SP500~DGS10 (60j) = 0.1472 -- 14.7% de la variance des rendements SP500 expliquee par les variations du taux 10 ans (le reste = idiosyncratique/autres facteurs)
- **test_chow** -- test de Chow (taux 10 ans, 1ere vs 2eme moitie des 12 derniers mois) : F=432.904, p=0.0000 -- RUPTURE structurelle significative
- **cointegration_secteurs** -- 0/10 secteurs cointegres avec SP500 -- decouples : ['XLK', 'XLF', 'XLE', 'XLV', 'XLI', 'XLY', 'XLP', 'XLU', 'XLB', 'XLRE']  _(sans synthese)_
