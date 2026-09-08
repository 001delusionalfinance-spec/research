"""Modele -- filtre de Kalman, modele a niveau local (random walk + bruit) sur le VIX.

x_t = x_(t-1) + w_t (niveau latent, marche aleatoire), y_t = x_t + v_t (observation bruitee) --
le niveau filtre EST une estimation de "ou est vraiment le VIX" en lissant le bruit
d'observation jour a jour, mise a jour de facon bayesienne a chaque nouvelle donnee (pas une
simple moyenne mobile a fenetre fixe). Implementation via `statsmodels.tsa.statespace.
UnobservedComponents` (Kalman filter + estimation MLE de Q/R integrees, pas reimplemente a la
main -- le filtre de Kalman lui-meme est standard, mais l'estimation robuste des variances de
bruit ne l'est pas assez pour le faire a la main sans risque).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, valeurs  # noqa: E402

NOM_MODELE = "kalman_niveau_local"


def main() -> int:
    try:
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    niveaux = valeurs(vix)
    date_du_jour = vix[-1][0]
    if len(niveaux) < 60:
        print("echec -- moins de 60 points, filtre non fiable")
        return 1

    from statsmodels.tsa.statespace.structural import UnobservedComponents

    modele = UnobservedComponents(niveaux, level="local level")
    resultat = modele.fit(disp=False)

    niveau_filtre = float(resultat.filtered_state[0][-1])
    variance_niveau = float(resultat.filtered_state_cov[0][0][-1])
    observation_brute = niveaux[-1]
    ecart_bruit = observation_brute - niveau_filtre

    sigma2_niveau = float(resultat.params[0])
    sigma2_observation = float(resultat.params[1])
    ratio_signal_bruit = sigma2_niveau / sigma2_observation if sigma2_observation > 0 else None

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "vix_observe", "vix_filtre_kalman", "ecart_type_filtre",
         "ratio_signal_bruit"],
        [[date_du_jour, observation_brute, round(niveau_filtre, 3),
          round(variance_niveau ** 0.5, 3),
          round(ratio_signal_bruit, 5) if ratio_signal_bruit is not None else ""]],
    )

    # ratio_signal_bruit = variance du niveau / variance d'observation : >1 -> le filtre
    # attribue le gros du mouvement au vrai niveau et suit les observations de pres (peu de
    # lissage) ; <1 -> il attribue le mouvement au bruit d'observation et lisse fortement
    # (le niveau filtre reagit lentement, s'ecarte plus de l'observation brute).
    if ratio_signal_bruit is not None and ratio_signal_bruit > 1:
        lecture_filtre = f"le filtre suit les observations de pres, peu de lissage (ecart obs.-filtre={ecart_bruit:+.2f})"
    elif ratio_signal_bruit is not None and ratio_signal_bruit < 1:
        lecture_filtre = f"le filtre lisse fortement le bruit, reagit lentement (ecart obs.-filtre={ecart_bruit:+.2f})"
    elif ratio_signal_bruit is not None:
        lecture_filtre = f"lissage equilibre entre signal et bruit (ecart obs.-filtre={ecart_bruit:+.2f})"
    else:
        lecture_filtre = None

    print(f"OK -- VIX observe={observation_brute:.2f}, filtre Kalman={niveau_filtre:.2f} "
          f"(ecart-type={variance_niveau**0.5:.2f}), ratio signal/bruit="
          f"{ratio_signal_bruit:.4f} -- {lecture_filtre}" if ratio_signal_bruit is not None else "N/A")
    return 0


if __name__ == "__main__":
    sys.exit(main())
