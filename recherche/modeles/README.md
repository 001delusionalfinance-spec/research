# recherche/modeles/

Code qui lit `donnees/brut/` et calcule — une lane par famille de recherche (voir `MAP.md` à la
racine pour le détail des 8 familles) :

`macro/` · `statistique/` · `series-temporelles/` · `factorielle/` · `risque/` ·
`positionnement-comportemental/` · `nlp/` · `ml/`

L'orchestrateur `run_all_modeles.py` appelle les modèles un à un : un échec isolé n'interrompt
jamais les autres. Les résultats sont publiés dans `rapports/`.
