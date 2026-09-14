"""Modele -- assouplissement et resserrement quantitatifs (QE / QT).

Mesure la variation des bilans de banques centrales. C'est la moitie de la politique monetaire
que le taux directeur ne dit pas : une banque centrale peut tenir son taux inchange et durcir
fortement en laissant son bilan se reduire.

Sources melangees a dessein -- Fed, BCE et Banque du Japon viennent de FRED, la Banque
d'Angleterre, la RBA et la Banque du Canada de leurs sites nationaux (`donnees/brut/bilans/`).

**Le point de methode qui compte** : les bilans sont exprimes dans des unites et des devises
differentes (millions de dollars, d'euros, de livres, de dollars australiens...). Les comparer
en niveau n'aurait aucun sens. Tout est donc ramene en **variation relative** -- sur 3 mois et
sur 12 mois -- ce qui est de toute facon la grandeur qui informe : ce n'est pas la taille du
bilan qui agit sur les marches, c'est son sens de variation et sa vitesse.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, ecrire_csv, read_series  # noqa: E402

NOM_MODELE = "bilans_banques_centrales"

# (libelle, chemin, colonne de valeur)
BILANS = [
    ("Fed -- actif total", BRUT / "fred" / "WALCL.csv", "value"),
    ("Fed -- titres du Tresor", BRUT / "fred" / "TREAST.csv", "value"),
    ("Fed -- titres hypothecaires", BRUT / "fred" / "WSHOMCB.csv", "value"),
    ("BCE -- actif total", BRUT / "fred" / "ECBASSETSW.csv", "value"),
    ("Banque du Japon -- actif total", BRUT / "fred" / "JPNASSETS.csv", "value"),
    ("Banque d'Angleterre -- bilan", BRUT / "bilans" / "BOE_BILAN_TOTAL.csv", "valeur"),
    ("RBA -- bilan", BRUT / "bilans" / "RBA_BILAN_TOTAL.csv", "valeur"),
    ("RBA -- titres locaux", BRUT / "bilans" / "RBA_TITRES_LOCAUX.csv", "valeur"),
    ("Banque du Canada -- actif total", BRUT / "bilans" / "BOC_V36610.csv", "valeur"),
]
SEUIL_MOUVEMENT_PCT = 1.0  # en deca sur 12 mois, bilan considere stable


def valeur_il_y_a(serie: list, jours: int) -> float:
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=jours)
    anterieurs = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not anterieurs:
        raise SerieVide(f"aucun point {jours} jours avant la derniere observation")
    return anterieurs[-1]


def main() -> int:
    lignes, echecs = [], []
    for libelle, chemin, colonne in BILANS:
        try:
            serie = read_series(chemin, colonne)
            niveau = serie[-1][1]
            if niveau == 0:
                raise SerieVide("dernier niveau nul -- variation relative non definie")
            var_3m = (niveau / valeur_il_y_a(serie, 91) - 1) * 100
            var_12m = (niveau / valeur_il_y_a(serie, 365) - 1) * 100
            if var_12m > SEUIL_MOUVEMENT_PCT:
                regime = "expansion (QE)"
            elif var_12m < -SEUIL_MOUVEMENT_PCT:
                regime = "reduction (QT)"
            else:
                regime = "stable"
            lignes.append((libelle, serie[-1][0], round(var_3m, 2), round(var_12m, 2), regime))
        except (SerieVide, ValueError, ZeroDivisionError) as e:
            echecs.append((libelle, str(e)))

    if not lignes:
        print(f"echec -- aucun bilan exploitable ({len(echecs)} en erreur)")
        return 1

    lignes.sort(key=lambda l: l[3])
    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["bilan", "date", "variation_3m_pct", "variation_12m_pct", "regime"], lignes)

    regimes = [l[4] for l in lignes]
    n_qt = regimes.count("reduction (QT)")
    n_qe = regimes.count("expansion (QE)")
    if n_qt and n_qe:
        lecture = (f"regimes OPPOSES -- {n_qt} bilan(s) en reduction pendant que {n_qe} "
                   f"s'etendent, la liquidite mondiale ne va pas dans un sens unique")
    elif n_qt > n_qe:
        lecture = "resserrement quantitatif dominant -- retrait de liquidite en cours"
    elif n_qe > n_qt:
        lecture = "expansion dominante -- apport de liquidite en cours"
    else:
        lecture = "bilans globalement stables"

    print(f"OK -- {len(lignes)} bilans suivis sur 12 mois : de {lignes[0][3]:+.1f}% "
          f"({lignes[0][0]}) a {lignes[-1][3]:+.1f}% ({lignes[-1][0]}) -- {lecture}")
    if echecs:
        print(f"   {len(echecs)} bilan(s) non exploitable(s) : {[n for n, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
