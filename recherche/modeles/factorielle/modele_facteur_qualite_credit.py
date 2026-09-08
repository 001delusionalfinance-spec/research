"""Modele -- facteur de qualite de credit : spread high-yield moins spread investment-grade
(BAMLH0A0HYM2 - BAMLC0A0CM), niveau et tendance.

Un ecart HY-IG qui se creuse = le marche exige une prime de risque croissante pour detenir du
credit de moins bonne qualite -- signal de "flight to quality" implicite dans les prix
obligataires, independant des mesures de positionnement (COT) ou de prix actions deja
construites ailleurs.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "facteur_qualite_credit"


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    if len(serie) < 2:
        raise SerieVide("pas assez de points")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not candidats:
        raise SerieVide(f"aucun point disponible {n_jours}j avant")
    return candidats[-1]


def main() -> int:
    try:
        hy = read_series(BRUT / "fred" / "BAMLH0A0HYM2.csv")
        ig = read_series(BRUT / "fred" / "BAMLC0A0CM.csv")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    dates_communes = sorted(set(d for d, _ in hy) & set(d for d, _ in ig))
    if not dates_communes:
        print("echec -- aucune date commune HY/IG")
        return 1

    map_hy, map_ig = dict(hy), dict(ig)
    date_du_jour = dates_communes[-1]
    ecart_actuel = map_hy[date_du_jour] - map_ig[date_du_jour]

    serie_ecart = [(d, map_hy[d] - map_ig[d]) for d in dates_communes]
    try:
        ecart_reference = valeur_n_jours_avant(serie_ecart, 182)
        tendance_pct = (ecart_actuel - ecart_reference) / abs(ecart_reference) * 100 \
            if ecart_reference else None
    except SerieVide:
        tendance_pct = None

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "spread_hy", "spread_ig", "ecart_hy_ig", "variation_6m_pct"],
        [[date_du_jour, map_hy[date_du_jour], map_ig[date_du_jour], round(ecart_actuel, 3),
          round(tendance_pct, 1) if tendance_pct is not None else ""]],
    )

    # niveau absolu : bandes indicatives sur l'ecart HY-IG (pas de reference precise) --
    # tendance : le sens de la variation 6m dit si le risque credit percu monte ou baisse
    if ecart_actuel < 3:
        niveau = "niveau contenu"
    elif ecart_actuel < 5:
        niveau = "niveau modere"
    else:
        niveau = "stress credit eleve"

    if tendance_pct is None:
        tendance_lecture = "tendance indisponible"
    elif tendance_pct > 0:
        tendance_lecture = "s'ecarte (risque credit percu en hausse)"
    elif tendance_pct < 0:
        tendance_lecture = "se resserre (risque credit percu en baisse)"
    else:
        tendance_lecture = "stable"

    print(f"OK -- spread HY={map_hy[date_du_jour]:.2f}, IG={map_ig[date_du_jour]:.2f}, "
          f"ecart={ecart_actuel:.2f}pt ({niveau}), variation 6m="
          f"{f'{tendance_pct:+.1f}%' if tendance_pct is not None else 'indisponible'} -- {tendance_lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
