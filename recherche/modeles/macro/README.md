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

## `modele_probabilite_reunion_fed.py` (2026-09-17)

Probabilité de mouvement du taux directeur US par horizon — PAS un arbre de probabilités par
réunion à la CME FedWatch (accès gratuit à la bande complète de futures Fed Funds fermé, CME
bloque explicitement le scraping de ses settlements, vérifié en direct). Combine deux lectures
gratuites et officielles : le contrat Fed Funds front-month (`ZQ=F`, Yahoo) pour le mois en
cours si une réunion y tombe, et un bootstrap de taux forward sur la courbe des bons du Trésor
(`DGS1MO/DGS3MO/DGS6MO/DGS1`) pour 4 fenêtres à terme (0-1, 1-3, 3-6, 6-12 mois) — mouvement NET
CUMULÉ par fenêtre, pas une probabilité isolée par réunion (`n_reunions_incluses` le rappelle à
chaque ligne). Calendrier des réunions FOMC ingéré séparément (`ingestion_fomc_calendrier.py`,
même page que les communiqués, lue différemment pour capter les dates à venir).

**Réserve trouvée en testant sur données réelles (2026-09-17), pas théorique** : les bons du
Trésor courts cotent 30 à 75 points de base AU-DESSUS du taux Fed effectif (`DFF`=3,63%,
`DGS1MO`=3,93%, `DGS1`=4,39%). Cet écart peut venir d'une vraie anticipation de marché
(pause/hausse) ou d'une prime technique d'offre de bills, sans rapport avec la politique
monétaire — une courbe OIS/SOFR propre séparerait les deux, elle n'est pas accessible
gratuitement (même blocage que les futures CME complets). Les lectures hausse/baisse des 4
fenêtres à terme sont donc à lire avec prudence ; la lecture `mois_en_cours` (via `ZQ=F`), elle,
n'a pas cette contamination.

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

## `modele_surprise_macro_composite.py` (2026-09-08)

Indice composite de surprise (esprit Citi Economic Surprise Index, 3 séries : chômage, crédit
bancaire, inflation) — proxy d'accélération vs tendance, pas un vrai consensus d'économistes
(donnée propriétaire non disponible). Testé réel : indice=-0,33 (surprises défavorables
dominent).

## `modele_balance_commerciale.py` (2026-09-08)

Balance commerciale US (`BOPGSTB`, ajouté à `ingestion_fred.py`). Testé réel : -88,6Md$,
rang percentile=1 (proche du déficit record historique), déficit qui se creuse.

## `modele_surprise_inflation.py` (2026-09-08)

Surprise CPI MoM vs prévision naïve (moyenne des 6 mois précédents) — complète le composite en
se concentrant sur l'inflation seule, en MoM plutôt qu'en YoY. Testé réel : surprise baissière
(-0,26pt).

**Macro complète les 12 idées de l'exercice initial** (Sahm, taux réel, Taylor, courbe US,
cycle crédit, conditions financières, REER, cycle immobilier, surprise composite, balance
commerciale, surprise inflation — seul le différentiel Fed dot-plot manque, donnée CME
FedWatch non accessible gratuitement).
