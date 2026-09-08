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
