# positionnement-comportemental/

Positionnement (CFTC COT), sentiment, proxy de crowding, information mutuelle. Voir `MAP.md`
(racine).

## `modele_positionnement_cot.py` (2026-09-08)

Z-score du positionnement net spéculatif (non-commercial) sur 9 marchés : S&P 500 (E-mini),
taux (UST 10Y), change (EUR/JPY/GBP + indice dollar), or, pétrole (WTI), volatilité (VIX
futures). Fenêtre de 78 semaines (~1,5 an), `|z| > 2` marque un positionnement extrême — lecture
contrarienne classique.

**Deux noms de contrat corrigés en vérifiant en direct (2026-09-08)** : les noms trouvés par
recherche de mots-clés dans l'API CFTC ("10-YEAR U.S. TREASURY NOTES...", "BRITISH POUND
STERLING...") n'avaient plus de données depuis 2022-02 — le nom courant du contrat a changé
("UST 10Y NOTE", "BRITISH POUND") sans que ce soit documenté ailleurs que dans les données
elles-mêmes. Détail dans `ingestion_cftc.py`.

Testé de bout en bout avec de vraies données (156 semaines par contrat, ingestion réelle sans
clé API requise).
