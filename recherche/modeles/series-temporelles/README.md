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
