"""Modele -- volatilite realisee (S&P 500, 5/20/60j) + volatilite EWMA (RiskMetrics,
lambda=0.94) et sa tendance recente.

Deux techniques deliberement differentes cote a cote : la vol realisee (fenetre fixe, chaque
jour pese pareil) et l'EWMA (poids decroissant exponentiellement, plus reactive) peuvent
diverger apres un choc recent -- l'ecart lui-meme est une information (l'EWMA "voit" un choc
plus vite que la vol realisee 60j).

Formule EWMA standard (RiskMetrics 1996) : sigma_t^2 = lambda*sigma_(t-1)^2 + (1-lambda)*r_t^2,
amorcee avec la variance des 20 premiers rendements de la fenetre disponible (1 an
d'historique, donc l'amorçage consomme le tout debut de la fenetre a chaque run -- pas ideal
mais explicite, a ameliorer si un historique plus long est ingere un jour).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import (BRUT, ETAT, SerieVide, accumuler_csv, lire_historique,  # noqa: E402
                   nouvelle_figure, read_series, rendements_log, sauvegarder_figure,
                   valeurs, vol_annualisee)

NOM_MODELE = "volatilite_ewma"
LAMBDA_EWMA = 0.94
FENETRES = [5, 20, 60]
JOURS_PAR_AN = 252


def vol_ewma(rendements: list, lam: float = LAMBDA_EWMA) -> float:
    """EWMA de la variance sur toute la serie de rendements donnee, annualisee -- amorcee sur
    les 20 premiers rendements (variance simple), puis recursive jusqu'au dernier point."""
    if len(rendements) < 21:
        raise SerieVide("pas assez de rendements pour amorcer l'EWMA (minimum 21)")
    variance = sum(r ** 2 for r in rendements[:20]) / 20
    for r in rendements[20:]:
        variance = lam * variance + (1 - lam) * r ** 2
    return (variance * JOURS_PAR_AN) ** 0.5


def tendance_ewma(historique: list, jours: int = 10) -> str:
    """'hausse'/'baisse'/'stable' sur les `jours` derniers runs accumules dans rapports/donnees/
    -- seuil relatif 10%, pas absolu (une vol a 10% qui monte a 11% n'est pas le meme mouvement
    qu'une vol a 30% qui monte a 33%, meme ecart en points)."""
    if len(historique) < jours + 1:
        raise SerieVide(f"moins de {jours + 1} runs accumules -- tendance pas encore mesurable")
    reference = float(historique[-jours - 1]["vol_ewma"])
    actuel = float(historique[-1]["vol_ewma"])
    ecart_relatif = (actuel - reference) / reference if reference else 0
    if ecart_relatif > 0.10:
        return "hausse"
    if ecart_relatif < -0.10:
        return "baisse"
    return "stable"


def tracer(chemin_csv) -> None:
    historique = lire_historique(chemin_csv)
    dates = [l["date"] for l in historique]
    vol60 = [float(l["vol_realisee_60j"]) for l in historique if l["vol_realisee_60j"]]
    ewma = [float(l["vol_ewma"]) for l in historique]

    plt, fig, ax = nouvelle_figure()
    if len(vol60) == len(dates):
        ax.plot(dates, vol60, color="#999999", linewidth=1.2, label="Vol realisee 60j")
    ax.plot(dates, ewma, color="black", linewidth=1.3, label="Vol EWMA (lambda=0.94)")
    ax.set_ylabel("Volatilite annualisee")
    ax.set_xticks(ax.get_xticks()[::max(1, len(ax.get_xticks()) // 8)])
    ax.tick_params(axis="x", rotation=45)
    ax.set_title("S&P 500 -- volatilite realisee vs EWMA")
    ax.legend(fontsize=8)
    sauvegarder_figure(plt, fig, NOM_MODELE, "volatilite_ewma")


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    date_du_jour = sp500[-1][0]
    rendements = rendements_log(prix)

    vols_realisees = {}
    for f in FENETRES:
        try:
            vols_realisees[f] = vol_annualisee(prix[-f - 1:]) if len(prix) > f else None
        except SerieVide:
            vols_realisees[f] = None

    try:
        vol_ewma_actuelle = vol_ewma(rendements)
    except SerieVide as e:
        print(f"echec EWMA -- {e}")
        return 1

    chemin_csv = ETAT / f"{NOM_MODELE}.csv"
    accumuler_csv(
        chemin_csv,
        ["date", "vol_ewma", "vol_realisee_5j", "vol_realisee_20j", "vol_realisee_60j"],
        [[date_du_jour, round(vol_ewma_actuelle, 4)] +
         [round(vols_realisees[f], 4) if vols_realisees[f] is not None else ""
          for f in FENETRES]],
    )

    try:
        tendance = tendance_ewma(lire_historique(chemin_csv))
    except SerieVide as e:
        tendance = f"indisponible ({e})"

    tracer(chemin_csv)
    print(f"OK -- vol realisee 60j={vols_realisees.get(60)}, EWMA={vol_ewma_actuelle:.4f} "
          f"(tendance 10 runs: {tendance})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
