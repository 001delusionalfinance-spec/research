# series-temporelles/

Regime-switching formel (HMM/Kalman, pas juste un seuil sur percentile), volatilité
conditionnelle (GARCH), saisonnalité. Voir `MAP.md` (racine).

## `modele_volatilite_ewma.py` (2026-09-08)

Volatilité réalisée S&P 500 (5/20/60j) + volatilité EWMA (RiskMetrics, lambda=0.94, poids
décroissant exponentiellement — plus réactive à un choc récent qu'une fenêtre fixe). Tendance
mesurée sur les 10 derniers runs accumulés dans `recherche/etat/` (10% de variation relative,
pas un seuil absolu).

Nécessite `ingestion_yfinance_indices.py` (SP500, VIX — même pattern d'appel direct à l'API
chart Yahoo que GMDC, vérifié fonctionnel et frais le 2026-09-08).

Testé avec de vraies données (vol réalisée 60j ≈ 11,8%, EWMA ≈ 10,4%, cohérent avec un VIX à
~15 le même jour) et la logique de classification de tendance testée sur des cas synthétiques
à résultat connu (hausse/stable/baisse) avant le test réel.

## `modele_garch.py` (2026-09-08)

GARCH(1,1) sur les rendements S&P 500 (librairie `arch`) — paramètres estimés par maximum de
vraisemblance, pas un lambda fixé comme l'EWMA. Piège connu et vérifié explicitement : la
librairie recommande des rendements ×100 pour la stabilité numérique, oublier de re-diviser
donne une vol ~100x trop grande (bug réel déjà trouvé par GMDC sur leur propre GARCH — évité
ici en comparant le résultat à la vol réalisée). Testé réel : 12,10% annualisée, persistance
0,921 — cohérent avec EWMA/réalisée.

## `modele_hurst.py` (2026-09-08)

Exposant de Hurst (analyse R/S, Mandelbrot 1968) — mesure si les rendements ont une mémoire
longue (H>0,5, tendanciel) ou courte (H<0,5, retour à la moyenne). **Limite réelle trouvée en
validant sur une marche aléatoire synthétique** (H théorique = 0,5) : le R/S simple a un biais
positif connu à échantillon fini, confirmé ici (H mesuré = 0,593 sur du vrai bruit gaussien).
Le résultat réel sur S&P 500 (H=0,608) est donc à peine au-dessus de ce biais — preuve de
mémoire plus faible que le chiffre brut ne le suggère.
