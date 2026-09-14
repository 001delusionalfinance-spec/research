"""Modele -- divergence des politiques monetaires entre les 12 blocs suivis.

Lit les taux directeurs quotidiens du BIS (`donnees/brut/bis/taux_directeurs/`) : le taux que
la banque centrale FIXE, pas un proxy interbancaire.

Ce que ca repond : ou en est chaque banque centrale dans son cycle, et de combien elles
s'ecartent les unes des autres. C'est la variable qui commande le change -- une paire est par
construction une comparaison entre deux politiques monetaires, et c'est l'ecart entre elles,
pas le niveau absolu de l'une, qui la fait bouger.

Trois mesures par bloc : le niveau, la variation sur 6 mois (le cycle en cours) et la variation
sur 12 mois. Une banque centrale a l'arret depuis un an ne se lit pas comme une qui vient de
baisser trois fois.
"""

import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, ecrire_csv, read_series  # noqa: E402

NOM_MODELE = "divergence_taux_directeurs"
TAUX_DIR = BRUT / "bis" / "taux_directeurs"

BLOCS = {
    "US": "Etats-Unis", "XM": "Zone euro", "GB": "Royaume-Uni", "JP": "Japon",
    "CH": "Suisse", "CA": "Canada", "AU": "Australie", "NZ": "Nouvelle-Zelande",
    "SE": "Suede", "NO": "Norvege", "KR": "Coree", "CN": "Chine",
}
SEUIL_MOUVEMENT_PT = 0.10  # en dessous, on considere la banque centrale a l'arret


def valeur_il_y_a(serie: list, jours: int) -> float:
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=jours)
    anterieurs = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not anterieurs:
        raise SerieVide(f"aucun point {jours} jours avant la derniere observation")
    return anterieurs[-1]


def main() -> int:
    lignes, echecs = [], []
    for code, nom in BLOCS.items():
        try:
            serie = read_series(TAUX_DIR / f"{code}.csv", "taux")
            niveau = serie[-1][1]
            var_6m = niveau - valeur_il_y_a(serie, 182)
            var_12m = niveau - valeur_il_y_a(serie, 365)
            if var_6m > SEUIL_MOUVEMENT_PT:
                cycle = "resserrement"
            elif var_6m < -SEUIL_MOUVEMENT_PT:
                cycle = "assouplissement"
            else:
                cycle = "pause"
            lignes.append((nom, code, serie[-1][0], round(niveau, 3),
                           round(var_6m, 3), round(var_12m, 3), cycle))
        except (SerieVide, ValueError) as e:
            echecs.append((nom, str(e)))

    if not lignes:
        print(f"echec -- aucun bloc exploitable ({len(echecs)} en erreur)")
        return 1

    lignes.sort(key=lambda l: -l[3])
    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["bloc", "code", "date", "taux_directeur_pct", "variation_6m_pt",
                "variation_12m_pt", "phase_de_cycle"], lignes)

    niveaux = [l[3] for l in lignes]
    ecart_max = max(niveaux) - min(niveaux)
    phases = [l[6] for l in lignes]
    n_resserrement = phases.count("resserrement")
    n_assouplissement = phases.count("assouplissement")
    n_pause = phases.count("pause")

    if n_resserrement and n_assouplissement:
        lecture = (f"cycles OPPOSES en cours -- {n_resserrement} banque(s) resserrent pendant "
                   f"que {n_assouplissement} assouplissent, configuration qui elargit "
                   f"mecaniquement les differentiels de taux")
    elif n_pause == len(lignes):
        lecture = "toutes a l'arret -- aucun moteur de divergence cote politique monetaire"
    else:
        sens = "resserrement" if n_resserrement else "assouplissement"
        lecture = f"cycles alignes dans le meme sens ({sens}) -- divergence limitee"

    print(f"OK -- {len(lignes)} banques centrales : ecart de taux max {ecart_max:.2f}pt "
          f"({lignes[0][0]} {lignes[0][3]:.2f}% contre {lignes[-1][0]} {lignes[-1][3]:.2f}%), "
          f"mediane {statistics.median(niveaux):.2f}% -- {lecture}")
    if echecs:
        print(f"   {len(echecs)} bloc(s) non exploitable(s) : {[n for n, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
