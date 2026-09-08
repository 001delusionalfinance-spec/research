# macro/

Régimes croissance/inflation par bloc économique, cycle de politique monétaire, courbes de
taux. Voir `MAP.md` (racine, section "Ce qui est recherché").

## `modele_regime_monetaire_emploi.py` (2026-09-08)

Premier modèle du dépôt. Classe 5 blocs (US, Zone euro, Royaume-Uni, Japon, Chine) sur deux
dimensions : tendance et niveau du taux directeur (ou proxy), tendance du taux de chômage.

**Volontairement pas un quadrant croissance/inflation classique.** Testé et documenté dans
`ingestion_fred.py` : l'inflation internationale (CPI) n'est pas disponible fraîche
gratuitement — les séries OCDE sur FRED ont couramment 12 à 60+ mois de retard (Allemagne
figée à 2025-04, Royaume-Uni à 2025-03, Japon à 2021-06, Chine à 2025-04, vérifié en direct le
2026-09-08). Le taux directeur et le chômage, en revanche, sont frais partout (Chine exceptée
pour le chômage — aucune série fiable trouvée sur FRED).

**À noter sur le "niveau relatif" (bas/moyen/haut)** : c'est un tercile calculé sur tout
l'historique disponible de la série, qui remonte parfois à une ère de taux proches de zéro
(zone euro 2014-2022). Un taux "haut" au sens de ce modèle veut dire haut par rapport à toute
l'histoire de la série, pas forcément par rapport aux 5 dernières années — à garder en tête en
le lisant.

## `modele_sahm_rule.py` (2026-09-08)

Règle de Sahm (Claudia Sahm, ex-Fed) : signal de récession US quand la moyenne mobile 3 mois du
chômage monte de 0,50 point ou plus par rapport à son plus bas sur 12 mois. Recalculée
directement depuis `UNRATE` déjà ingéré. Testé sur cas synthétique (série stable puis choc de
chômage) avant le test réel — se déclenche correctement. État réel du jour : non déclenchée
(chômage US stable à 4,1%).

## `modele_taux_reel_us.py` (2026-09-08)

Taux directeur US nominal (`DFF`) moins inflation CPI en glissement annuel (`CPIAUCSL`) — la
condition monétaire réelle, pas juste le chiffre affiché. Limite assumée : inflation *réalisée*
(ex post), pas anticipée (ex ante) — un vrai taux réel ex ante utiliserait les breakevens
(non ingérés ici). Testé réel : nominal 3,63%, inflation YoY 3,30%, réel +0,33%.

## `modele_regle_taylor.py` (2026-09-08)

Règle de Taylor (1993), version à 2 termes (r*=2%, cible inflation=2%, sans le terme d'écart de
production — aucun PIB potentiel ingéré, terme omis et documenté plutôt qu'approximé par un
proxy inventé). Testé réel : taux recommandé=5,96%, Fed réelle=3,63% — écart -2,33pt
(accommodant selon la règle).

## `modele_courbe_taux_us.py` (2026-09-08)

Spread 10 ans - 2 ans (`DGS10`/`DGS2`, ajoutés à `ingestion_fred.py`) — un des signaux de
récession macro les plus suivis (Estrella & Mishkin 1998). Suit aussi la durée de
l'inversion, pas juste son état instantané. Testé réel : spread=+0,43pt, courbe normale.

## `modele_cycle_credit.py` (2026-09-08)

Croissance annuelle du crédit bancaire total US (`TOTBKCR`, Fed H.8, ajouté à `ingestion_fred.py`).
Testé réel : +6,34% YoY, 40,9e percentile de son propre historique — normal.

## `modele_conditions_financieres.py` (2026-09-08)

Indice composite simplifié (esprit Chicago Fed NFCI, 3 composantes : taux directeur, courbe
inversée, VIX) — chaque composante déjà utilisée ailleurs, la valeur ajoutée est la combinaison.
Testé réel : indice=-0,14 (conditions proches de la normale, légèrement accommodantes).

## `modele_reer_us.py` (2026-09-08)

Taux de change effectif réel US (BIS, `RBUSBIS`) — ajusté de l'inflation relative, contrairement
à USD_INDEX (positionnement nominal déjà suivi). Testé réel : rang percentile=94 (dollar réel
fort, compétitivité réduite).

## `modele_cycle_immobilier.py` (2026-09-08)

Mises en chantier, permis de construire, taux hypothécaire 30 ans (`HOUST`/`PERMIT`/
`MORTGAGE30US` ajoutés à `ingestion_fred.py`) — les permis précèdent les chantiers dans le
processus réel, comparaison de tendance pour un signal avancé. Testé réel : pas de divergence
(les deux en baisse ensemble).
