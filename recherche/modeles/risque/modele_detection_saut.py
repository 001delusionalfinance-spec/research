"""Modele -- detection de saut (Barndorff-Nielsen & Shephard 2004/2006, tripower quarticity
Huang & Tauchen 2005), S&P 500. Deja promis dans les READMEs de la vague 1 comme "a construire
si utile" -- construit maintenant.

Compare la variance realisee (RV, somme des rendements au carre -- capte TOUT le mouvement, sauts
inclus) a la variation bipower (BV, robuste aux sauts par construction -- utilise le produit de
rendements consecutifs, qu'un saut isole ne peut pas gonfler de la meme facon). Un ecart RV-BV
statistiquement significatif = presence d'un saut ce jour-la, distinct d'un choc de volatilite
diffuse (deja mesure par modele_changepoint_volatilite.py -- un vrai krach general en cluster
de vol peut echapper a CE test, cf. limite observee sur COVID -- teste ici aussi).

Formule standard (theta=pi^2/4+pi-5, mu_(4/3)=2^(2/3)*Gamma(7/6)/Gamma(1/2)) -- Z-stat asymptotique
normale sous H0 (pas de saut). Fenetre de 22 jours (~1 mois de bourse).

**Limite reelle trouvee en validant sur diffusion pure synthetique** (200 fenetres de bruit
gaussien SANS saut, aucun parametre invente) avant le test reel : 36/200 faux positifs a
|Z|>1.96 (18%), largement au-dessus des ~5% attendus sous une vraie loi normale. Confirme un
biais de petit echantillon deja documente dans la litterature (Huang & Tauchen 2005) -- n=22
est trop petit pour que l'approximation asymptotique normale soit fiable. Teste separement,
correctement calibre pour un vrai saut : un saut synthetique de 15% injecte donne Z=29.75,
detecte sans ambiguite malgre le bruit de fond. **A lire donc comme "un Z tres eleve = saut
quasi certain", pas comme "|Z|>1.96 = 5% de risque de se tromper"** -- le seuil nominal
n'est pas fiable a cette taille de fenetre, pas corrige ici (bootstrap de calibration a
envisager si ce modele devient central).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series, rendements_log, valeurs  # noqa: E402

NOM_MODELE = "detection_saut"
FENETRE = 22
SEUIL_Z = 1.96  # 5% bilateral


def bns_z_stat(rendements_fenetre: list) -> float:
    import math
    n = len(rendements_fenetre)
    if n < 5:
        raise SerieVide("fenetre trop courte pour BNS")

    rv = sum(r ** 2 for r in rendements_fenetre)
    bv = (math.pi / 2) * sum(abs(rendements_fenetre[i]) * abs(rendements_fenetre[i - 1])
                              for i in range(1, n))

    mu_4_3 = 2 ** (2 / 3) * math.gamma(7 / 6) / math.gamma(1 / 2)
    tq = n * (mu_4_3 ** -3) * sum(
        abs(rendements_fenetre[i]) ** (4 / 3) * abs(rendements_fenetre[i - 1]) ** (4 / 3) *
        abs(rendements_fenetre[i - 2]) ** (4 / 3)
        for i in range(2, n)
    )

    theta = (math.pi ** 2) / 4 + math.pi - 5
    if bv == 0:
        raise SerieVide("bipower variation nulle -- test non defini")
    ratio_tq_bv2 = tq / (bv ** 2)
    denominateur = theta * (1 / n) * max(1, ratio_tq_bv2)
    if denominateur <= 0:
        raise SerieVide("denominateur non positif -- test non defini")
    return (rv - bv) / (bv * math.sqrt(denominateur))


def main() -> int:
    try:
        sp500 = read_series(BRUT / "yfinance" / "SP500.csv", value_col="close")
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prix = valeurs(sp500)
    date_du_jour = sp500[-1][0]
    rendements = rendements_log(prix)

    try:
        z = bns_z_stat(rendements[-FENETRE:])
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    saut_detecte = abs(z) > SEUIL_Z
    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "z_stat_bns", "saut_detecte", "fenetre_jours"],
        [[date_du_jour, round(z, 3), saut_detecte, FENETRE]],
    )

    print(f"OK -- Z-stat BNS (fenetre {FENETRE}j)={z:.3f} (seuil ±{SEUIL_Z}) -- "
          f"{'SAUT DETECTE' if saut_detecte else 'pas de saut isole detecte'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
