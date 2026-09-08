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
entre -0,951 et -0,777 sur la fenêtre d'historique disponible.
