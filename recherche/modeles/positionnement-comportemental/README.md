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

## `modele_momentum_positionnement.py` (2026-09-08)

Dérivée du z-score, pas son niveau : un z-score qui vient de passer de 0 à +1,5 en 8 semaines
(positionnement qui SE CONSTRUIT) n'est pas la même situation qu'un z-score déjà stabilisé à
+1,5. Testé réel : les 9 marchés ont un momentum de positionnement mesuré, aucun aberrant.

## `modele_crowding_cross_asset.py` (2026-09-08)

Combien de marchés ont un positionnement tendu (`|z|≥1,5`) **simultanément** — un risque de
déroulement corrélé que regarder un marché à la fois ne montre pas. Testé réel : 2/9 marchés
tendus au même moment (EUR_FX court, USD_INDEX long — cohérent, même thème dollar fort).

## `modele_divergence_cot_prix.py` (2026-09-08)

Divergence classique : prix qui monte pendant que le positionnement spéculatif net recule.
Limité à S&P 500 pour l'instant — seul marché où `donnees/brut/` a à la fois un prix
(`yfinance/SP500.csv`) et un positionnement (`cftc/SP500_EMINI.csv`). Testé réel : pas de
divergence actuellement (SP500 -0,86% sur 30j, COT net déjà en baisse dans le même sens).

## `modele_ratio_commercial_speculatif.py` (2026-09-08)

Ratio |position commerciale nette| / |position spéculative nette|, 9 marchés — les
"commercial" du rapport COT couvrent en théorie une exposition réelle, souvent à l'opposé des
spéculateurs. Nécessite les colonnes `comm_long`/`comm_short` ajoutées à `ingestion_cftc.py`
(2026-09-08). Testé réel : 7/9 marchés en sens opposé commercial/spéculatif (cohérent avec la
théorie) — EUR_FX et SP500_EMINI font exception, à surveiller.

## `modele_rotation_risk_on_off.py` (2026-09-08)

Z-score moyen actifs risque (SP500_EMINI, NASDAQ_MINI) vs refuge (GOLD, UST_10Y) — nécessite
NASDAQ_MINI, ajouté à `ingestion_cftc.py` (vérifié frais). Testé réel : posture mixte/neutre.

## `modele_concentration_traders.py` (2026-09-08)

Position nette moyenne par trader — proxy de concentration, pas un vrai Herfindahl (le rapport
COT legacy ne publie pas les positions individuelles, limite assumée dès le départ). Nécessite
les colonnes `traders_*` ajoutées à `ingestion_cftc.py`. Testé réel sur 11 marchés, ex. UST_10Y
la plus concentrée (2110/trader), EUR_FX la moins (78/trader).

## `modele_metaux_precieux.py` (2026-09-08)

Positionnement comparé or/argent/platine — nécessite SILVER/PLATINUM, ajoutés à
`ingestion_cftc.py`. Testé réel : écart or/industriels=+1,40 (or plus tendu que les deux
autres).

## `modele_persistance_extremes.py` (2026-09-08)

Depuis combien de semaines consécutives le z-score reste extrême, 13 marchés (nécessite
`SILVER`/`PLATINUM`/`NASDAQ_MINI`/`COPPER`, tous ajoutés récemment). Testé réel : USD_INDEX
extrême depuis 12 semaines consécutives, la plus longue persistance actuelle.
