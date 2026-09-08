"""Modele -- analyse spectrale (periodogramme, FFT) du VIX -- cherche des cycles dominants
dans la serie, au-dela du retour a la moyenne deja mesure par modele_ornstein_uhlenbeck_vix.py.

FFT sur les rendements (pas les niveaux -- une serie non-stationnaire en niveau, cf. discipline
deja appliquee ailleurs, fausserait le spectre avec une fausse frequence dominante pres de 0).
Rapporte les 3 periodes les plus fortes du spectre de puissance -- une periode qui revient
souvent proche d'un cycle connu (~21j = un mois de bourse, ~63j = un trimestre) serait un signal
de saisonnalite reelle, pas juste du bruit.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs  # noqa: E402

NOM_MODELE = "analyse_spectrale"


def main() -> int:
    try:
        vix = read_series(BRUT / "yfinance" / "VIX.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    niveaux = valeurs(vix)
    date_du_jour = vix[-1][0]
    rendements = rendements_log(niveaux)
    if len(rendements) < 200:
        print("echec -- moins de 200 rendements")
        return 1

    import numpy as np

    n = len(rendements)
    rendements_centres = np.array(rendements) - np.mean(rendements)
    fft_result = np.fft.rfft(rendements_centres)
    puissance = np.abs(fft_result) ** 2
    frequences = np.fft.rfftfreq(n, d=1.0)  # d=1 jour de bourse

    # ignore la frequence 0 (la moyenne, deja retiree, et les tres basses frequences pres de 0
    # qui dominent artificiellement toute serie financiere bruitee -- cf. 1/f noise connu)
    indices_valides = np.where(frequences > 1.0 / 252)[0]  # exclut les cycles > 1 an
    if len(indices_valides) < 3:
        print("echec -- pas assez de frequences exploitables")
        return 1

    puissance_valide = puissance[indices_valides]
    frequences_valides = frequences[indices_valides]
    ordre = np.argsort(puissance_valide)[::-1][:3]

    top3 = []
    for idx in ordre:
        freq = float(frequences_valides[idx])
        periode_jours = 1.0 / freq if freq > 0 else None
        top3.append((round(periode_jours, 1) if periode_jours else None,
                      float(puissance_valide[idx])))

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "periode_1_jours", "puissance_1", "periode_2_jours", "puissance_2",
         "periode_3_jours", "puissance_3"],
        [[date_du_jour] + [v for pair in top3 for v in
                            (pair[0], round(pair[1], 2))]],
    )

    print(f"OK -- 3 periodes dominantes (jours de bourse) : {[p[0] for p in top3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
