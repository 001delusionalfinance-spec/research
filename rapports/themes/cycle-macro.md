# Croissance, inflation et cycle macro

Activite, emploi, inflation, immobilier, commerce et finances publiques.

Mis a jour : **2026-10-06 19:28 UTC** · 9 lectures.

[Retour au tableau de bord](../README.md)

### Sahm rule

MM3 chomage=4.13%, plus bas 12m=4.13%, ecart=0.00pt (seuil 0.5pt) -- non declenchee

_Statut **OK** · observation 2026-09-01 · moteur `macro` · [donnees](../donnees/sahm_rule.csv)_


### Cycle immobilier

mises en chantier=1275.0k (baisse), permis=1403.0k (stable), taux hypothecaire=7.28% -- pas de divergence

_Statut **OK** · observation 2026-08-01 · moteur `macro` · [donnees](../donnees/cycle_immobilier.csv)_


### Inflation comparee

inflation annuelle sur 12 blocs : mediane 3.06%, dispersion 3.75pt (Nouvelle-Zelande +4.06% au plus haut, Suede +0.31% au plus bas) -- dispersion forte -- les banques centrales sont poussees a diverger, ce qui deplace les differentiels de taux et le change

_Statut **OK** · observation non exposee par la sortie · moteur `macro` · [donnees](../donnees/inflation_comparee.csv) · [graphique](../graphiques/inflation_comparee/apercu.png)_


### Activite zone euro

zone euro : Production industrielle -0.2 % sur 12 mois, Ventes de detail +0.9 % sur 12 mois, Taux de chomage +0.1 pt sur 12 mois, Confiance industrielle +2.7 pt vs moyenne longue -- production industrielle DIVERGENTE entre grands pays -- en hausse : Espagne ; en baisse : Allemagne, France, Italie

_Statut **OK** · observation non exposee par la sortie · moteur `macro` · [donnees](../donnees/activite_zone_euro.csv)_


### Soutenabilite dette

8 pays. charge la plus lourde : Canada a 25.5% du revenu. taux 10 ans AU-DESSUS de l'inflation dans 5 pays -- Royaume-Uni (+2.3pt), Etats-Unis (+1.9pt), Japon (+1.2pt), Canada (+0.9pt), Zone euro (+0.9pt). Configuration ou le ratio d'endettement monte meme a budget primaire equilibre (approximation : croissance nominale reduite a l'inflation)

_Statut **OK** · observation non exposee par la sortie · moteur `macro` · [donnees](../donnees/soutenabilite_dette.csv)_


### Matieres premieres macro

le ratio cuivre/or monte -- la croissance domine la peur (+6.8% sur 3 mois). Brent 100.9$ (+36.1% sur 3 mois, +54.1% sur 12 mois), gaz -4.4% sur 3 mois, ecart Brent-WTI +11.2$ -- energie nettement plus chere sur un an -- pression inflationniste a venir que les prix a la consommation ne montrent pas encore

_Statut **OK** · observation 2026-10-06 · moteur `macro` · [donnees](../donnees/matieres_premieres_macro.csv) · [graphique](../graphiques/matieres_premieres_macro/apercu.png)_


### Surprise macro composite

indice de surprise macro=-1.00 ({'chomage': -1, 'credit_bancaire': -1, 'inflation': -1}) -- negatif (surprises defavorables dominent)

_Statut **OK** · observation 2026-09-01 · moteur `macro` · [donnees](../donnees/surprise_macro_composite.csv)_


### Balance commerciale

balance commerciale=-105,572M$ (rang percentile=1), deficit se creuse

_Statut **OK** · observation 2026-08-01 · moteur `macro` · [donnees](../donnees/balance_commerciale.csv)_


### Surprise inflation

CPI MoM=+0.396%, prevision naive=+0.316%, surprise=+0.080pt -- surprise haussiere (inflation plus forte qu'attendu)

_Statut **OK** · observation 2026-08-01 · moteur `macro` · [donnees](../donnees/surprise_inflation.csv)_

