# paper-trading/

Une thèse validée (voir `theses/`) devient ici une construction de trade concrète : instrument,
sizing, condition d'invalidation. Exécutée sur un compte IBKR **paper** (aucun capital réel),
suivie jusqu'à clôture avec un vrai blotter et de vraies métriques de performance (TWR/Sharpe/
drawdown — même logique que `metriques_performance.py` dans GMDC, mais ici mesurée pour
apprendre, pas pour un book réel). Voir `MAP.md` (racine, famille 10).

**Angle mort ouvert, à trancher avant de construire** : un repo `claude-portfolio-manager`
existe déjà (connectivité IBKR paper vérifiée bout en bout le 2026-09-04, jamais utilisé) —
à décider si on réutilise cette connectivité ou si on construit la sienne ici.

Rien construit pour l'instant.
