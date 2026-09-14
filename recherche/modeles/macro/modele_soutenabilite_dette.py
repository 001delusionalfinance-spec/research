"""Modele -- soutenabilite de la dette : le stock, la charge, et la condition de derive.

Trois lectures que le stock de dette seul ne donne pas.

**1. Le stock** -- dette publique en % du PIB (Eurostat pour la zone euro et ses grands pays,
FRED pour les Etats-Unis).

**2. La charge** -- ratio de service de la dette du secteur prive non financier (BIS, 12 pays).
Un stock eleve a taux bas se porte ; le meme stock a taux eleve etrangle. C'est le service, pas
le stock, qui dit si la dette pese reellement.

**3. La condition de derive** -- comparaison du taux souverain 10 ans a la croissance nominale
approchee par l'inflation. Quand le taux payé sur la dette depasse durablement la croissance
nominale, le ratio d'endettement monte mecaniquement meme a budget primaire equilibre : c'est
l'effet boule de neige. Approximation assumee et signalee : la croissance nominale est ici
reduite a l'inflation, faute de PIB reel ingere pour les 12 blocs -- le signe du differentiel
reste informatif, son niveau exact non.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, ecrire_csv, read_series  # noqa: E402

NOM_MODELE = "soutenabilite_dette"

# (pays, dette % PIB, service de la dette BIS, souverain 10a, indice de prix BIS)
PAYS = [
    ("Etats-Unis", BRUT / "fred" / "GFDEGDQ188S.csv", "value",
     BRUT / "bis" / "service_dette" / "US.csv", BRUT / "fred" / "DGS10.csv", "value", "US"),
    ("Zone euro", BRUT / "eurostat" / "dette_publique" / "EA20.csv", "valeur",
     None, BRUT / "souverains" / "ZONE_EURO_TOUS_10A.csv", "taux", "XM"),
    ("Royaume-Uni", None, None,
     BRUT / "bis" / "service_dette" / "GB.csv", BRUT / "souverains" / "UK_10A.csv", "taux", "GB"),
    ("Japon", None, None,
     BRUT / "bis" / "service_dette" / "JP.csv", BRUT / "souverains" / "JAPON_10A.csv",
     "taux", "JP"),
    ("Allemagne", BRUT / "eurostat" / "dette_publique" / "DE.csv", "valeur",
     BRUT / "bis" / "service_dette" / "DE.csv", None, None, None),
    ("France", BRUT / "eurostat" / "dette_publique" / "FR.csv", "valeur",
     BRUT / "bis" / "service_dette" / "FR.csv", None, None, None),
    ("Italie", BRUT / "eurostat" / "dette_publique" / "IT.csv", "valeur",
     BRUT / "bis" / "service_dette" / "IT.csv", None, None, None),
    ("Canada", None, None,
     BRUT / "bis" / "service_dette" / "CA.csv", BRUT / "souverains" / "CANADA_10A.csv",
     "taux", "CA"),
]


def _dernier(chemin, colonne):
    if chemin is None:
        return None
    try:
        return read_series(chemin, colonne)[-1][1]
    except (SerieVide, ValueError):
        return None


def _inflation_annuelle(code):
    if code is None:
        return None
    try:
        serie = read_series(BRUT / "bis" / "cpi" / f"{code}.csv", "indice")
    except (SerieVide, ValueError):
        return None
    derniere = serie[-1][0]
    annee, reste = derniere.split("-")[0], derniere.split("-")[1]
    ref = [v for p, v in serie if p == f"{int(annee) - 1}-{reste}"]
    return (serie[-1][1] / ref[0] - 1) * 100 if ref else None


def main() -> int:
    lignes = []
    for (nom, p_dette, c_dette, p_service, p_taux, c_taux, code_prix) in PAYS:
        dette = _dernier(p_dette, c_dette)
        service = _dernier(p_service, "ratio")
        taux = _dernier(p_taux, c_taux)
        inflation = _inflation_annuelle(code_prix)
        differentiel = (taux - inflation) if (taux is not None and inflation is not None) else None
        if dette is None and service is None and differentiel is None:
            continue
        lignes.append((nom,
                       round(dette, 1) if dette is not None else "",
                       round(service, 2) if service is not None else "",
                       round(taux, 2) if taux is not None else "",
                       round(inflation, 2) if inflation is not None else "",
                       round(differentiel, 2) if differentiel is not None else ""))

    if not lignes:
        print("echec -- aucun pays exploitable")
        return 1

    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["pays", "dette_publique_pct_pib", "service_dette_privee_pct",
                "souverain_10a_pct", "inflation_annuelle_pct",
                "differentiel_taux_moins_inflation_pt"], lignes)

    derives = [(l[0], l[5]) for l in lignes if l[5] != "" and l[5] > 0]
    services = [(l[0], l[2]) for l in lignes if l[2] != ""]
    services.sort(key=lambda t: -t[1])

    if derives:
        noms = ", ".join(f"{n} ({v:+.1f}pt)" for n, v in sorted(derives, key=lambda t: -t[1]))
        lecture = (f"taux 10 ans AU-DESSUS de l'inflation dans {len(derives)} pays -- {noms}. "
                   f"Configuration ou le ratio d'endettement monte meme a budget primaire "
                   f"equilibre (approximation : croissance nominale reduite a l'inflation)")
    else:
        lecture = ("taux 10 ans partout sous l'inflation -- configuration qui allege "
                   "mecaniquement le poids de la dette")

    charge = (f"charge la plus lourde : {services[0][0]} a {services[0][1]:.1f}% du revenu"
              if services else "service de la dette non disponible")
    print(f"OK -- {len(lignes)} pays. {charge}. {lecture}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
