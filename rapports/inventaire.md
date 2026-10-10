# Inventaire du dispositif -- 2026-10-10 01:16 UTC

Genere par `inventaire.py`. **Ne pas recopier ces chiffres ailleurs** : ils changent a chaque ajout, et une copie manuelle derive le jour meme (constate le 2026-09-14).

## Donnees ingerees

| Source | Fichiers |
|---|---|
| FRED (series officielles) | 76 |
| BIS -- prix a la consommation | 12 |
| BIS -- taux directeurs quotidiens | 12 |
| BIS -- service de la dette | 12 |
| Courbes souveraines quotidiennes | 26 |
| Marches (FX, matieres, vol, indices) | 33 |
| Eurostat | 30 |
| Bilans de banques centrales | 29 |
| Positionnement CFTC | 32 |
| Tresor US | 3 |
| Indices et secteurs (yfinance) | 12 |
| **Total** | **281** |

Fraicheur : 275 ok, 2 suspecte.

## Modeles

| Famille | Modeles |
|---|---|
| factorielle | 13 |
| macro | 21 |
| ml | 12 |
| nlp | 13 |
| positionnement-comportemental | 14 |
| risque | 13 |
| series-temporelles | 13 |
| statistique | 13 |
| **Total** | **112** |

## Sorties

- 116 fichiers de donnees (`rapports/donnees/`)
- 26 graphiques utiles (`rapports/graphiques/`)
- `rapports/lecture-du-jour.md`, `rapports/etat-recherche.xlsx`
