"""Modele -- rotation entre marches actions mondiaux.

Compare la performance des indices par bloc economique (S&P 500, Euro Stoxx 50, Nikkei, FTSE,
DAX, KOSPI, Hang Seng) sur 3 et 12 mois.

Ce que ca repond : **l'argent va-t-il vers un bloc en particulier ?** Un ecart de performance
durable entre zones traduit soit une divergence de cycle economique, soit un flux de capitaux
transfrontalier -- deux choses qui se lisent aussi dans les taux et le change, et dont la
confirmation croisee vaut mieux qu'un signal isole.

**Limite importante et non contournee ici** : les indices sont en devise locale. Une hausse du
Nikkei de 10% avec un yen qui perd 10% ne rapporte rien a un investisseur en dollars. La
performance en devise locale mesure la dynamique economique domestique ; elle ne mesure PAS le
rendement d'un investisseur etranger. Les deux lectures sont legitimes, celle-ci est la
premiere -- convertir demanderait d'apparier chaque indice a sa paire de change, ce qui est
faisable avec les donnees ingerees mais reste un autre modele.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, ecrire_csv, read_series  # noqa: E402

NOM_MODELE = "indices_mondiaux"
IDX = BRUT / "marches" / "indices"

INDICES = [
    ("Etats-Unis (S&P 500)", BRUT / "yfinance" / "SP500.csv"),
    ("Zone euro (Euro Stoxx 50)", IDX / "EUROSTOXX50.csv"),
    ("Allemagne (DAX)", IDX / "DAX.csv"),
    ("Royaume-Uni (FTSE 100)", IDX / "FTSE100.csv"),
    ("Japon (Nikkei 225)", IDX / "NIKKEI225.csv"),
    ("Coree (KOSPI)", IDX / "KOSPI.csv"),
    ("Hong Kong (Hang Seng)", IDX / "HANGSENG.csv"),
]
SEUIL_ECART_PCT = 10.0


def valeur_il_y_a(serie: list, jours: int) -> float:
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=jours)
    anterieurs = [v for d, v in serie if date.fromisoformat(d) <= cible]
    if not anterieurs:
        raise SerieVide(f"aucun point {jours} jours avant")
    return anterieurs[-1]


def main() -> int:
    lignes, echecs = [], []
    for libelle, chemin in INDICES:
        try:
            serie = read_series(chemin, "close")
            niveau = serie[-1][1]
            var_3m = (niveau / valeur_il_y_a(serie, 91) - 1) * 100
            var_12m = (niveau / valeur_il_y_a(serie, 365) - 1) * 100
            lignes.append((libelle, serie[-1][0], round(niveau, 2),
                           round(var_3m, 2), round(var_12m, 2)))
        except (SerieVide, ValueError, ZeroDivisionError) as e:
            echecs.append((libelle, str(e)))

    if not lignes:
        print(f"echec -- aucun indice exploitable ({len(echecs)} en erreur)")
        return 1

    lignes.sort(key=lambda l: -l[4])
    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["indice", "date", "niveau", "variation_3m_pct", "variation_12m_pct"], lignes)

    meilleur, pire = lignes[0], lignes[-1]
    ecart_12m = meilleur[4] - pire[4]
    # Le classement a-t-il change entre 3 et 12 mois ? C'est ca, une rotation.
    ordre_3m = [l[0] for l in sorted(lignes, key=lambda l: -l[3])]
    tete_3m, tete_12m = ordre_3m[0], meilleur[0]

    if ecart_12m > SEUIL_ECART_PCT * 2:
        dispersion = (f"ecart tres large entre blocs sur 12 mois ({ecart_12m:.0f}pt) -- les "
                      f"cycles economiques ou les flux divergent nettement")
    elif ecart_12m > SEUIL_ECART_PCT:
        dispersion = f"ecart notable entre blocs sur 12 mois ({ecart_12m:.0f}pt)"
    else:
        dispersion = f"blocs groupes sur 12 mois ({ecart_12m:.0f}pt d'ecart)"

    if tete_3m != tete_12m:
        rotation = (f". ROTATION en cours : {tete_12m} mene sur 12 mois mais {tete_3m} a repris "
                    f"la tete sur 3 mois")
    else:
        rotation = f". Pas de rotation : {tete_12m} mene sur les deux horizons"

    print(f"OK -- {len(lignes)} indices (devise locale) : {meilleur[0]} {meilleur[4]:+.1f}% en "
          f"tete sur 12 mois, {pire[0]} {pire[4]:+.1f}% en queue -- {dispersion}{rotation}")
    if echecs:
        print(f"   {len(echecs)} indice(s) non exploitable(s) : {[n for n, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
