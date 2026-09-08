# recherche/modeles/

Code qui lit `donnees/brut/` et calcule — une lane par famille de recherche (voir `MAP.md` à la
racine pour le détail des 10 familles) :

`macro/` · `statistique/` · `series-temporelles/` · `factorielle/` · `risque/` ·
`positionnement-comportemental/` · `nlp/` · `ml/`

Les familles 9 (thèse) et 10 (paper trading) ne sont pas des modèles calculés — elles vivent
dans `theses/` et `paper-trading/` à la racine.

Rien construit pour l'instant. Une fois les premiers modèles écrits, un orchestrateur
(`run_all_modeles.py`, même principe que GMDC : un échec isolé n'interrompt jamais les autres)
viendra ici.
