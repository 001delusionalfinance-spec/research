# ml/

Walk-forward strict uniquement — discipline anti-overfitting
(validation sur données synthétiques à paramètres connus avant tout test réel ; un modèle qui
ne bat pas une baseline naïve se documente honnêtement, ne se cache pas). Voir `MAP.md`
(racine).

## `modele_walkforward_direction.py` (2026-09-08)

Prédiction de la direction (hausse/baisse) du S&P 500 à J+1, walk-forward strict (pour prédire
un jour, n'utilise jamais une donnée postérieure) : règle simple de momentum de continuation à
5 jours, comparée à une baseline de classe majoritaire (elle aussi calculée uniquement sur le
passé disponible à chaque étape). Aucune librairie ML — stdlib seulement, la logique testée sur
cas synthétiques à résultat connu avant le test réel.

**Résultat honnête** : sur 470 prédictions walk-forward (2 ans d'historique
initial), momentum 5j = 48,30% de précision, baseline majoritaire = 55,74% — **le momentum NE
BAT PAS la baseline**. Recalculé depuis l'extension à 30 ans (2026-09-08 après-midi, voir
`risque/modele_stress_test_historique.py`) sur 7516 prédictions : 49,63% vs 53,78% — même
verdict, confirmé sur un échantillon bien plus large. Rapporté tel quel, pas ajusté pour
paraître mieux.

## `modele_anomalie_multivariee.py` (2026-09-08)

Distance de Mahalanobis (rendement SP500 + variation VIX conjoints) — une anomalie CONJOINTE
(les deux dimensions ensemble), pas juste un gros mouvement isolé sur une seule. Calcul à la
main (pas de sklearn), **validé contre `scipy.spatial.distance.mahalanobis` sur données
synthétiques avant le test réel** (résultat identique au 4e chiffre). Testé réel : distance
0,549 (seuil 3.0) — jour ordinaire.

## `modele_test_overfitting.py` (2026-09-08)

Démonstration explicite d'overfitting : la même famille de règle (momentum sur N jours) est
d'abord "optimisée" en cherchant le meilleur N sur tout l'historique à la fois (in-sample,
l'erreur classique d'un backtest naïf), puis réévaluée avec ce N en walk-forward strict.
L'écart entre les deux EST la démonstration. Testé réel : écart quasi nul (+0,0002 sur
30 ans d'historique) — pas de signature forte d'overfitting sur cet échantillon, résultat
rapporté tel quel plutôt qu'un écart plus spectaculaire qui aurait mieux illustré le propos.

## `modele_prevision_vol_regression.py` (2026-09-08)

Prévision de volatilité par régression AR(1) simple (rendement au carré ~ rendement au carré
de la veille), split train/test strict 70/30 (coefficients fittés uniquement sur train, jamais
re-fittés en voyant le test). Comparée à une baseline "persistance" (prédire le rendement au
carré de demain = celui d'aujourd'hui), pas directement à GARCH/EWMA (comparaison MSE contre un
rendement au carré brut, très bruyant, ne serait pas équitable pour des modèles qui prévoient
une variance lissée — limite documentée). Testé réel : la régression BAT la baseline
(MSE 2,98e-07 vs 3,83e-07) — résultat honnête, positif cette fois.

## `modele_screening_features.py` (2026-09-08)

Screening préalable à tout modèle combiné : corrélation univariée (test point-bisérial) de
4 features candidates (momentum 5j/20j, niveau VIX, variation VIX) avec la direction J+1 du
S&P 500. Un modèle de kfold-vs-walk-forward avait été tenté puis **abandonné en testant** : pour
une règle fixe non apprise, mélanger l'ordre d'évaluation ne change rien à l'accuracy (testé,
écart quasi nul confirmé) — un vrai test de fuite k-fold demanderait un paramètre RÉ-APPRIS par
fold, pas encore construit, remplacé par ce screening plus simple et honnête.

**Bug réel de fuite temporelle trouvé et corrigé le 2026-09-08 (vague 7)** : le résultat
original (vague 2, déjà mergé) donnait `variation_vix` fortement significative (r=-0,51,
p<0,0001) — ce chiffre a été cité comme signal fort dans plusieurs docstrings dérivées avant
d'être découvert comme un artefact. `variation_vix[i]` utilisait `niveaux_vix[i+1] -
niveaux_vix[i]`, soit le MÊME intervalle temporel que la direction prédite (`dirs[i]` = prix[i]
vs prix[i+1]) — de l'information du futur, pas du passé. Trouvé en construisant
`modele_decision_stump.py` (accuracy walk-forward suspecte de 78,9%, bien au-delà de tout ce qui
est plausible). Corrigé : `variation_vix[i] = niveaux_vix[i] - niveaux_vix[i-1]` (mouvement de
la veille, réellement connu avant de prédire). **Résultat corrigé, réel** : variation_vix
r=+0,0306, p=0,0079 — statistiquement non-nul sur ce grand échantillon mais négligeable en
pratique (loin du r=-0,51 d'origine). momentum_5j faiblement significatif (r=-0,03, p=0,01),
momentum_20j et niveau_vix non significatifs.

## `modele_kmeans_regimes.py` (2026-09-08)

K-means (k=3, implémentation à la main, validée à 100% de pureté sur cas synthétique à 3
clusters connus) sur VIX/spread de courbe/taux directeur — découvre les régimes plutôt que de
les définir a priori. Testé réel : 3 clusters de tailles 3195/3486/807 sur 30 ans de données.

## `modele_ensemble_signaux.py` (2026-09-08)

Vote majoritaire momentum_5j + variation_vix (suite de `modele_screening_features.py`), walk-forward
strict. Testé réel, résultat honnête et surprenant : même le signal VIX seul (fort en
corrélation univariée) ne bat pas la baseline en classification binaire — corrélation continue
et précision de classification binaire ne se traduisent pas automatiquement l'une en l'autre.

## `modele_couts_transaction.py` (2026-09-08)

Impact de frais simulés (5pb/changement de position) sur la stratégie momentum 5j walk-forward.
**Bug réel trouvé en testant** : sommer des rendements journaliers simples sur 30 ans donnait
un nombre sans interprétation directe (-208%) — corrigé en calculant une vraie courbe de
performance composée. Testé réel après correction : -92,81% brut, -96,62% net (cohérent avec
l'accuracy déjà connue, sous la baseline).

## `modele_regression_multifeatures.py` (2026-09-08)

Régression multi-features (momentum 5j + variation VIX ensemble, pas testées séparément comme
dans le screening) sur le rendement J+1, split train/test 70/30 strict. Testé réel : R²
out-of-sample=0,0102 — positif mais modeste, le modèle bat la moyenne de peu.

## `modele_stacking.py` (2026-09-08)

Stacking : poids de combinaison momentum+baseline APPRIS (régression logistique par descente de
gradient, split train/test strict), pas un vote fixe comme `modele_ensemble_signaux.py`. Testé
réel, résultat honnête : le poids appris pour momentum est quasi nul, le modèle converge vers
la baseline seule — confirme une fois de plus que le signal prix seul n'apporte rien ici.

## `modele_decision_stump.py` (2026-09-08, vague 7)

Decision stump (seuil unique appris sur `variation_vix`, la brique de base d'un arbre/forêt) —
teste si un seuil non-linéaire simple capture quelque chose qu'une droite ne capture pas. Seuil
cherché uniquement sur le train (déciles), jamais recalculé en voyant le test.

**C'est ce modèle qui a révélé le bug de fuite temporelle de `modele_screening_features.py`** :
premier test avec la feature buguée (`niveaux_vix[i+1]-niveaux_vix[i]`) donnait 78,89%
d'accuracy walk-forward — largement au-delà de tout ce qui est plausible sur ce type de
relation, ce qui a déclenché l'investigation. Une fois `variations_vix` corrigé dès l'écriture
(`niveaux_vix[i]-niveaux_vix[i-1]`, réellement connu avant la prédiction), **résultat honnête** :
accuracy stump=54,73% vs baseline=54,90% sur 2264 points test — le stump NE BAT PAS la baseline,
cohérent avec tout le reste de cette famille sur la relation SP500/VIX contemporaine.

## `modele_importance_permutation.py` (2026-09-08, vague 7)

Importance de feature par permutation (Breiman 2001) sur le modèle déjà fitté de
`modele_regression_multifeatures.py` — mesure de combien le R² out-of-sample se dégrade quand on
mélange aléatoirement une feature à la fois dans le test set, donc l'importance DANS le modèle
combiné (effets partagés/redondants inclus), pas seulement le lien univarié déjà mesuré par le
screening. Feature `variation_vix` construite ici avec le décalage correct dès l'origine (même
pattern que `modele_regression_multifeatures.py`, vérifié non affecté par le bug ci-dessus).
Testé réel : R² base=0,0102 — importance momentum5j=0,00771, importance variation_vix=0,01416 —
le VIX contribue davantage au modèle combiné que le momentum, malgré un R² global modeste.
