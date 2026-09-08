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

**Résultat honnête, comme dans GMDC** : sur 470 prédictions walk-forward, momentum 5j =
48,30% de précision, baseline majoritaire = 55,74% — **le momentum NE BAT PAS la baseline**.
Rapporté tel quel, pas ajusté pour paraître mieux. Confirme la même mise en garde que GMDC
avait déjà trouvée sur un signal ML différent : un signal simple sur prix seul n'a pas
d'avantage démontré ici.

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
L'écart entre les deux EST la démonstration. Testé réel : écart quasi nul (+0,0009) — pas de
signature forte d'overfitting sur cet échantillon, résultat rapporté tel quel plutôt qu'un
écart plus spectaculaire qui aurait mieux illustré le propos.
