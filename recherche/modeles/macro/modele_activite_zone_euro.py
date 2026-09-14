"""Modele -- activite reelle de la zone euro et de ses quatre grands pays membres.

Lit les series Eurostat (`donnees/brut/eurostat/`) : production industrielle, ventes de detail,
chomage et confiance industrielle, pour la zone euro et l'Allemagne, la France, l'Italie,
l'Espagne.

Ce que ca repond : l'economie europeenne accelere-t-elle ou ralentit-elle, et **les grands pays
membres vont-ils dans le meme sens**. Une zone euro stable en agregat peut recouvrir une
Allemagne en recession et une Espagne en expansion -- ce qui ne se pilote pas de la meme facon
avec un taux unique.

Sur la confiance industrielle : c'est un solde d'opinion, donc negatif la plupart du temps. Ce
qui informe est sa VARIATION et son ecart a sa propre moyenne longue, pas son signe.
"""

import statistics
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, ecrire_csv, read_series  # noqa: E402

NOM_MODELE = "activite_zone_euro"
EURO = BRUT / "eurostat"

INDICATEURS = [
    ("production_industrielle", "Production industrielle", "variation"),
    ("ventes_detail", "Ventes de detail", "variation"),
    ("chomage", "Taux de chomage", "niveau_inverse"),
    ("confiance_industrielle", "Confiance industrielle", "ecart_moyenne"),
]
GEOS = {"EA21": "Zone euro", "DE": "Allemagne", "FR": "France",
        "IT": "Italie", "ES": "Espagne"}


def valeur_il_y_a(serie: list, jours: int) -> float:
    def _d(p):
        annee, mois = p.split("-")[0], p.split("-")[1]
        return date(int(annee), int(mois), 1)
    cible = _d(serie[-1][0]) - timedelta(days=jours)
    anterieurs = [v for p, v in serie if _d(p) <= cible]
    if not anterieurs:
        raise SerieVide(f"aucun point {jours} jours avant")
    return anterieurs[-1]


def main() -> int:
    lignes, echecs = [], []
    for dossier, libelle, mode in INDICATEURS:
        for code, pays in GEOS.items():
            chemin = EURO / dossier / f"{code}.csv"
            try:
                serie = read_series(chemin, "valeur")
                niveau = serie[-1][1]
                if mode == "ecart_moyenne":
                    # Solde d'opinion : l'ecart a sa propre moyenne longue est la seule lecture
                    # honnete d'un indicateur qui vit en territoire negatif.
                    longue = statistics.mean([v for _, v in serie])
                    mesure, unite = niveau - longue, "pt vs moyenne longue"
                else:
                    ancien = valeur_il_y_a(serie, 365)
                    if ancien == 0:
                        raise SerieVide("valeur de reference nulle")
                    mesure = ((niveau / ancien - 1) * 100 if mode == "variation"
                              else niveau - ancien)
                    unite = "% sur 12 mois" if mode == "variation" else "pt sur 12 mois"
                lignes.append((libelle, pays, serie[-1][0], round(niveau, 2),
                               round(mesure, 2), unite))
            except (SerieVide, ValueError, ZeroDivisionError) as e:
                echecs.append((f"{libelle} {pays}", str(e)))

    if not lignes:
        print(f"echec -- aucun indicateur exploitable ({len(echecs)} en erreur)")
        return 1

    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["indicateur", "pays", "periode", "niveau", "mesure", "unite"], lignes)

    # Lecture d'ensemble : la production industrielle des quatre grands pays va-t-elle dans le
    # meme sens ? C'est la question qui distingue un ralentissement de zone d'un cas isole.
    prod = {l[1]: l[4] for l in lignes if l[0] == "Production industrielle" and l[1] != "Zone euro"}
    en_hausse = [p for p, v in prod.items() if v > 0]
    en_baisse = [p for p, v in prod.items() if v <= 0]
    if prod and en_hausse and en_baisse:
        lecture = (f"production industrielle DIVERGENTE entre grands pays -- en hausse : "
                   f"{', '.join(en_hausse)} ; en baisse : {', '.join(en_baisse)}")
    elif en_baisse and not en_hausse:
        lecture = "production industrielle en baisse dans tous les grands pays membres"
    elif en_hausse and not en_baisse:
        lecture = "production industrielle en hausse dans tous les grands pays membres"
    else:
        lecture = "production industrielle non exploitable ce jour"

    zone = {l[0]: (l[4], l[5]) for l in lignes if l[1] == "Zone euro"}
    resume = ", ".join(f"{nom} {v:+.1f} {u}" for nom, (v, u) in zone.items())
    print(f"OK -- zone euro : {resume} -- {lecture}")
    if echecs:
        print(f"   {len(echecs)} serie(s) non exploitable(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
