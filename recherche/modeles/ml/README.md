# ml/

Walk-forward strict uniquement — même discipline anti-overfitting déjà démontrée dans GMDC
(validation sur données synthétiques à paramètres connus avant tout test réel ; un modèle qui
ne bat pas une baseline naïve se documente honnêtement, ne se cache pas). Voir `MAP.md`
(racine).

## `modele_walkforward_direction.py` (2026-09-08)

Prédiction de la direction (hausse/baisse) du S&P 500 à J+1, walk-forward strict (pour prédire
un jour, n'utilise jamais une donnée postérieure) : règle simple de momentum de continuation à
5 jours, comparée à une baseline de classe majoritaire (elle aussi calculée uniquement sur le
passé disponible à chaque étape). Aucune librairie ML — stdlib seulement, la logique testée sur
cas synthétiques à résultat connu avant le test réel.

**Résultat honnête, comme dans GMDC** : sur 470 prédictions walk-forward (2 ans d'historique
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
fold, pas encore construit, remplacé par ce screening plus simple et honnête. Testé réel :
variation_vix fortement significative (r=-0,51, p<0,0001), momentum_5j faiblement significatif
(r=-0,03, p=0,01), momentum_20j et niveau_vix non significatifs.

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
