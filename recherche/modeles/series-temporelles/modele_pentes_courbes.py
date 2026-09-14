"""Modele -- pentes des courbes souveraines, tous blocs suivis.

Lit les courbes quotidiennes (`donnees/brut/souverains/`) plus la courbe americaine cote FRED,
et calcule la pente 2 ans / 10 ans pour chaque bloc, son niveau actuel et sa variation sur
3 mois.

Ce que ca repond : la pente dit ce que le marche anticipe de la politique monetaire a venir, la
ou le taux directeur ne dit que le present. Une courbe qui se repentifie par l'avant (le 2 ans
baisse plus vite que le 10 ans) signale des baisses de taux attendues ; une repentification par
l'arriere (le 10 ans monte) signale plutot une prime de terme qui se reconstitue -- offre de
papier souverain, risque d'inflation. Les deux se ressemblent sur un graphique de pente et
n'ont rien a voir, d'ou la decomposition en variations des deux jambes.

Une pente negative (inversion) est le signal recessif le plus documente de la litterature
macro-financiere ; elle est signalee explicitement.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, ecrire_csv, read_series  # noqa: E402

NOM_MODELE = "pentes_courbes"
SOUV = BRUT / "souverains"

# (bloc, chemin 2 ans, colonne, chemin 10 ans, colonne)
COURBES = [
    ("Etats-Unis", BRUT / "fred" / "DGS2.csv", "value", BRUT / "fred" / "DGS10.csv", "value"),
    ("Zone euro", SOUV / "ZONE_EURO_AAA_2A.csv", "taux",
     SOUV / "ZONE_EURO_AAA_10A.csv", "taux"),
    ("Japon", SOUV / "JAPON_2A.csv", "taux", SOUV / "JAPON_10A.csv", "taux"),
    ("Canada", SOUV / "CANADA_2A.csv", "taux", SOUV / "CANADA_10A.csv", "taux"),
    ("Australie", SOUV / "AUSTRALIE_2A.csv", "taux", SOUV / "AUSTRALIE_10A.csv", "taux"),
    ("Suede", SOUV / "SUEDE_2A.csv", "taux", SOUV / "SUEDE_10A.csv", "taux"),
    # Royaume-Uni : pas de 2 ans ingere, on prend le 5 ans comme jambe courte. Ecart signale
    # dans la sortie -- une pente 5s10s n'est pas comparable telle quelle a une 2s10s.
    ("Royaume-Uni (5s10s)", SOUV / "UK_5A.csv", "taux", SOUV / "UK_10A.csv", "taux"),
]
SEUIL_VARIATION_PT = 0.10


def valeur_il_y_a(serie: list, jours: int) -> float:
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=jours)
    anterieurs = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not anterieurs:
        raise SerieVide(f"aucun point {jours} jours avant")
    return anterieurs[-1]


def main() -> int:
    lignes, echecs = [], []
    for bloc, p_court, c_court, p_long, c_long in COURBES:
        try:
            court, long_ = read_series(p_court, c_court), read_series(p_long, c_long)
            pente = long_[-1][1] - court[-1][1]
            pente_3m = valeur_il_y_a(long_, 91) - valeur_il_y_a(court, 91)
            variation = pente - pente_3m
            var_court = court[-1][1] - valeur_il_y_a(court, 91)
            var_long = long_[-1][1] - valeur_il_y_a(long_, 91)

            if variation > SEUIL_VARIATION_PT:
                # Repentification : par l'avant si la jambe courte a plus baisse que la longue
                # n'a monte -- ce n'est pas le meme mecanisme.
                moteur = ("par l'avant (jambe courte en baisse -- baisses de taux attendues)"
                          if var_court < 0 and abs(var_court) >= abs(var_long)
                          else "par l'arriere (jambe longue en hausse -- prime de terme)")
                mouvement = f"repentification {moteur}"
            elif variation < -SEUIL_VARIATION_PT:
                mouvement = "aplatissement"
            else:
                mouvement = "stable"

            lignes.append((bloc, court[-1][0], round(court[-1][1], 3), round(long_[-1][1], 3),
                           round(pente, 3), round(variation, 3), round(var_court, 3),
                           round(var_long, 3), mouvement,
                           "inversee" if pente < 0 else "normale"))
        except (SerieVide, ValueError) as e:
            echecs.append((bloc, str(e)))

    if not lignes:
        print(f"echec -- aucune courbe exploitable ({len(echecs)} en erreur)")
        return 1

    lignes.sort(key=lambda l: l[4])
    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["bloc", "date", "taux_court_pct", "taux_long_pct", "pente_pt",
                "variation_pente_3m_pt", "variation_jambe_courte_3m_pt",
                "variation_jambe_longue_3m_pt", "mouvement", "forme"], lignes)

    inversees = [l[0] for l in lignes if l[9] == "inversee"]
    if inversees:
        lecture = (f"courbe INVERSEE dans {len(inversees)} bloc(s) : {', '.join(inversees)} -- "
                   f"le marche y anticipe des baisses de taux, signal recessif classique")
    else:
        lecture = "aucune courbe inversee -- pas de signal recessif par la pente"

    print(f"OK -- {len(lignes)} courbes : pente de {lignes[0][4]:+.2f}pt ({lignes[0][0]}) a "
          f"{lignes[-1][4]:+.2f}pt ({lignes[-1][0]}) -- {lecture}")
    if echecs:
        print(f"   {len(echecs)} courbe(s) non exploitable(s) : {[n for n, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
