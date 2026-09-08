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
