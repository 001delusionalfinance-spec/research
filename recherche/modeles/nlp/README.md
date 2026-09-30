# nlp/

Discours de banques centrales, minutes FOMC/BCE, texte réglementaire (10-K/10-Q si un module
single-name est un jour ajouté). Voir `MAP.md` (racine).

## `modele_ton_fomc.py` (2026-09-08)

Diff de ton entre les 2 derniers communiqués FOMC (source officielle federalreserve.gov,
`ingestion_fomc_statements.py`) : score de ton en pour-mille (lexique de ~30 mots construit à
la main), + changement de taux cible et de
vote (unanimité vs dissidents, noms extraits).

**Trois bugs réels trouvés en testant sur les 2 vrais communiqués** (2026-06-17, 2026-07-29),
documentés en tête de `ingestion_fomc_statements.py` : encodage mal deviné par `requests`
(tiret cadratin illisible), décompte de voix cherché hors des bornes du texte extrait, et
extraction des dissidents cassée par le point d'une initiale de milieu de nom ("Beth M.
Hammack"). Bug de chemin aussi trouvé et corrigé dans `modele_ton_fomc.py` — même classe
d'erreur que dans `ingestion_fred.py`/`ingestion_cftc.py` (compter les `parents[N]` à la main
plutôt que réutiliser `BRUT` de `_lib.py`), plus visible ici car le fichier est un niveau plus
profond (`nlp/` sous `modeles/`).

Testé avec de vraies données, résultat réel et cohérent : juin unanime (12-0), juillet 9-3 avec
3 dissidents nommés qui voulaient RELEVER les taux — vrai basculement hawkish du comité,
capturé correctement (pas un exemple inventé).

## `modele_frequence_mots_cles_fomc.py` (2026-09-08)

Fréquence de mots-clés précis (ex. "transitory", "patient", "data-dependent") dans le
communiqué le plus récent — plus granulaire que le score de ton agrégé, un mot spécifique a
parfois plus de portée qu'un score global. Testé réel : "uncertainty"×1, "elevated"×2,
"solid"×1, "strong"×1 présents dans le communiqué de juillet.

## `modele_complexite_texte_fomc.py` (2026-09-08)

Longueur/complexité du texte (mots, phrases, part de mots longs) comme proxy d'incertitude
rédactionnelle du comité — hypothèse testable, pas une certitude. Testé réel : 149 mots,
10 phrases, 14,9 mots/phrase, 32,9% de mots longs (>6 lettres).

## `modele_ton_minutes_fomc.py` (2026-09-08)

Même méthode que `ton_fomc.py`, appliquée aux **minutes** (pas le communiqué) — un document
~30x plus long (~4700 mots vs ~150), la discussion interne relativement moins polie que le
message public choisi mot à mot. Nouvelle source : `ingestion_fomc_minutes.py`
(`/monetarypolicy/fomcminutes<date>.htm`, marqueurs de début/fin vérifiés sur les 2 dernières
minutes réelles). Testé réel : ton +2,49‰ → +3,97‰ (diff +1,49‰).

## `modele_ecart_communique_minutes.py` (2026-09-08)

Écart de ton entre le communiqué (public) et les minutes (interne) de la MÊME réunion — aucune
nouvelle ingestion, réutilise les deux sources déjà en place. Testé réel, résultat marquant :
communiqué +13,42‰ vs minutes +3,97‰ (écart +9,45‰) — le message public est nettement plus
positif que la discussion interne de la même réunion.

## `modele_complexite_texte_minutes.py` (2026-09-08)

Mêmes métriques que `complexite_texte_fomc.py`, appliquées aux minutes (~30x plus long).
Testé réel : 4780 mots, 231 phrases, 20,7 mots/phrase, 35,6% de mots longs.

## `modele_entites_geographiques_minutes.py` (2026-09-08)

Fréquence de mentions géographiques/thématiques (comptage de mots-clés, pas un vrai NER) dans
les minutes — SUR QUOI le comité se concentre, complète le score de ton. Testé réel : inflation
mentionnée 51 fois, Middle East 12 fois, tariffs 7 fois.

## `modele_similarite_vocabulaire_minutes.py` (2026-09-08)

Indice de Jaccard entre les vocabulaires des 2 dernières minutes — combien le vocabulaire
change, indépendamment du ton. Testé réel : Jaccard=0,52 (368 mots nouveaux, 228 disparus).

## `modele_lisibilite_flesch_kincaid.py` (2026-09-08)

Indice Flesch-Kincaid (Reading Ease + Grade Level) réel — remplace le proxy "part de mots longs"
par une formule académique reconnue (comptage de syllabes heuristique, ~90% de précision sans
dictionnaire phonétique complet, validé sur 8 mots-tests avant le réel : 7/8 corrects). Testé
réel : communiqué Reading Ease=48,6 (niveau université) vs minutes=28,8 (nettement plus
difficile).

## `modele_frequence_mots_cles_minutes.py` (2026-09-08, vague 7)

Parallèle de `modele_frequence_mots_cles_fomc.py` (comptage de mots-clés thématiques),
appliqué aux minutes plutôt qu'au communiqué — même lexique, texte ~30x plus long. Testé réel
avec succès sur les minutes disponibles.

## `modele_langage_prudence.py` (2026-09-08, vague 7)

Indice de langage prudent/qualificatif ("hedging language" : however, likely, may, could,
appeared...) dans les minutes — distinct du score de ton (positif/négatif) et des mots-clés
thématiques : ici le DEGRÉ DE CERTITUDE du langage, indépendant de sa charge. Testé réel : 74
mots de prudence sur 4780 (15,48 pour mille).

## `modele_intensite_desaccord.py` (2026-09-08, vague 7)

Combine le nombre de dissidents formels au vote (déjà extrait du communiqué) avec la fréquence
de vocabulaire de désaccord dans les minutes ("disagreed", "preferred", "some participants"...)
— un désaccord peut exister sans dissidence formelle au vote. Testé réel : 3 dissident(s) au
vote, 20 mention(s) de désaccord dans le texte des minutes.
