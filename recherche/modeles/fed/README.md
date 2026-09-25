# Vue thématique Fed

Cette couche présente les modèles existants selon cinq questions : position actuelle, fonction
de réaction, anticipations de marché, liquidité/bilan et communication. Elle ne remplace ni les
modèles ni leurs historiques ; elle construit un contrat de sortie stable dans `rapports/fed/`.

Chaque mesure expose sa valeur, sa date, sa source, sa fraîcheur, son statut, son niveau de
confiance et sa méthodologie. Le dashboard ou toute autre interface doit lire cette couche plutôt
que les 115 fichiers d'état directement.
