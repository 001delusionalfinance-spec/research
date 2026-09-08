# statistique/

Corrélations avec test de significativité (pas de r affiché sans p-valeur), cointégration,
garde-fou multiple-testing (Bonferroni ou équivalent) dès qu'on scanne plusieurs paires à la
fois. Voir `MAP.md` (racine).

## `modele_correlations_positionnement.py` (2026-09-08)

Corrélations croisées du positionnement spéculatif (COT) entre les 9 marchés de
`positionnement-comportemental/` — aucune nouvelle ingestion, réutilise `donnees/brut/cftc/`.
36 paires testées, correction de Bonferroni appliquée (`_lib.seuils_bonferroni`).

Testé avec de vraies données : 20/36 paires significatives au run de test (ex. VIX_FUT/
WTI_CRUDE r=+0.52, EUR_FX/SP500_EMINI r=-0.54) — chiffres réels, pas un résultat inventé pour
l'exemple.

## `modele_stationnarite_taux.py` (2026-09-08)

Test ADF (Augmented Dickey-Fuller, via `statsmodels`) sur les 5 taux directeurs — garde-fou
méthodologique manquant jusqu'ici (corréler/régresser des séries non-stationnaires peut
produire une relation fallacieuse, Granger & Newbold 1974). Testé réel : 2/5 séries
stationnaires (US, Chine), 3/5 non-stationnaires (zone euro, UK, Japon) — à garder en tête
avant d'utiliser ces séries telles quelles ailleurs.

## `modele_correlation_glissante.py` (2026-09-08)

Corrélation S&P 500/VIX en fenêtre glissante 60j (sur les rendements, pas les niveaux) — montre
comment la relation évolue, pas juste sa valeur actuelle. Testé réel : -0,805 actuellement,
entre -0,955 et -0,429 sur les 30 ans d'historique désormais disponibles.

## `modele_cointegration_taux.py` (2026-09-08)

Test d'Engle-Granger (via `statsmodels`) entre chaque paire de taux directeurs — distinct de la
corrélation : deux séries peuvent partager un équilibre de LONG TERME sans être corrélées à
court terme. **Bug réel trouvé en écrivant le modèle** (pas en le testant après coup) : aligner
les séries par simple troncature "derniers N points de chaque série" aurait comparé des dates
différentes (fréquences quotidienne vs mensuelle mélangées) — corrigé par alignement explicite
sur les dates communes avant tout test. Testé réel : 4/10 paires cointégrées (toutes impliquant
la Chine).

## `modele_pca_taux.py` (2026-09-08)

PCA sur les 5 taux directeurs, aux dates communes — combien de "facteurs" indépendants
expliquent le mouvement conjoint des banques centrales (adaptation de Litterman-Scheinkman
1991, maturités → blocs). Calcul direct par eigendecomposition (numpy), pas sklearn. Testé
réel : 208 dates communes, 1ère composante explique 82,8% de la variance — poids dominant sur
UK/US/zone euro, quasi nul sur le Japon.

## `modele_clustering_marches.py` (2026-09-08)

Clustering hiérarchique (average linkage, scipy) des 11 marchés COT par distance de corrélation.
Testé réel : 4 clusters — {COPPER,GBP_FX,VIX_FUT,WTI_CRUDE}, {JPY_FX,UST_10Y},
{EUR_FX,NASDAQ_MINI,SP500_EMINI,USD_INDEX}, {GOLD} seul.

## `modele_causalite_granger.py` (2026-09-08)

Test de Granger (statsmodels, 5 lags) entre variation VIX et rendement SP500, les deux sens.
Précision terminologique importante dans le docstring : "causalité" de Granger = ordre
temporel prédictif, pas causalité structurelle. Testé réel : SP500→VIX significatif (p=0,004),
VIX→SP500 non (p=0,078).
