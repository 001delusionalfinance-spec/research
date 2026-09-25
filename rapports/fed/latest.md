# Fed Research

**État global : WARNING** · données au 2026-09-22

> ⚠️ Le chemin de taux dérivé des Treasuries ne constitue pas une distribution de probabilités par réunion FOMC.
> ⚠️ BIS en retard sur la derniere decision; le communique FOMC reste la source canonique jusqu'a resorption de l'ecart

## Position actuelle

| Mesure | Valeur | Date | Statut | Confiance | Source |
|---|---:|---|---|---|---|
| Milieu de la cible FOMC | 3.875 % | 2026-09-16 | ok | haute | Federal Reserve/FOMC |
| Taux Fed effectif | 3.88 % | 2026-09-18 | stale | haute | FRED DFF |
| Taux réel ex post | 0.527 % | 2026-09-18 | ok | moyenne | FRED DFF et CPIAUCSL |
| Cohérence FOMC / BIS | 0.25 point | 2026-09-25 | warning | haute | FOMC et BIS WS_CBPOL |

## Fonction de réaction

| Mesure | Valeur | Date | Statut | Confiance | Source |
|---|---:|---|---|---|---|
| Écart Fed - Taylor | -2.15 point | 2026-09-18 | ok | faible | Modèle Taylor interne |
| Écart règle de Sahm | 0 point | 2026-08-01 | stale | haute | FRED UNRATE |
| Conditions financières | 0.091 score z | 2026-09-18 | stale | moyenne | Composite interne |
| Surprise inflation | 0.08 point | 2026-08-01 | stale | faible | FRED CPIAUCSL |

## Anticipations de marché

| Mesure | Valeur | Date | Statut | Confiance | Source |
|---|---:|---|---|---|---|
| Mouvement implicite 0-1 mois | 9 pb | 2026-09-22 | ok | faible | forward_treasury_proxy |
| Mouvement implicite 1-3 mois | 34.5 pb | 2026-09-22 | ok | faible | forward_treasury_proxy |
| Mouvement implicite 3-6 mois | 46 pb | 2026-09-22 | ok | faible | forward_treasury_proxy |
| Mouvement implicite 6-12 mois | 76 pb | 2026-09-22 | ok | faible | forward_treasury_proxy |
| Pente Treasury 10a-2a | 0.25 point | 2026-09-18 | stale | haute | FRED DGS10/DGS2 |

## Liquidité et bilan

| Mesure | Valeur | Date | Statut | Confiance | Source |
|---|---:|---|---|---|---|
| Liquidité nette Fed | 5545717 M$ | 2026-09-16 | ok | moyenne | Fed H.4.1 via FRED |
| Variation liquidité sur 3 mois | 0.46 % | 2026-09-16 | ok | moyenne | Fed H.4.1 via FRED |

## Communication

| Mesure | Valeur | Date | Statut | Confiance | Source |
|---|---:|---|---|---|---|
| Variation du ton FOMC | 21.975 ‰ | 2026-09-16 | ok | faible | Communiqués FOMC |
| Dissidents au vote | 0 membres | 2026-09-16 | ok | haute | Communiqué FOMC |
| Mentions de désaccord | 20 mentions | 2026-07-29 | ok | faible | Minutes FOMC |

## Convention

Le chemin de taux est un **proxy de mouvement net**, pas une probabilité par réunion. `warning` signale une source retardée ou un proxy fragile ; `stale` signale une observation plus ancienne que sa cadence attendue.
