# nlp/

Discours de banques centrales, minutes FOMC/BCE, texte réglementaire (10-K/10-Q si un module
single-name est un jour récupéré depuis GMDC). Voir `MAP.md` (racine).

## `modele_ton_fomc.py` (2026-09-08)

Diff de ton entre les 2 derniers communiqués FOMC (source officielle federalreserve.gov,
`ingestion_fomc_statements.py`) : score de ton en pour-mille (lexique de ~30 mots construit à
la main, même logique que `nlp_earnings_diff.py` dans GMDC), + changement de taux cible et de
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
