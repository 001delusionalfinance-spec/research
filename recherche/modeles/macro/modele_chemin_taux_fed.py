"""Modele -- chemin de taux Fed implicite, lecture par horizon.

**Ce n'est PAS un arbre de probabilites par reunion a la CME FedWatch.** Le nom historique
``probabilite_reunion_fed`` etait donc trompeur : une courbe de taux donne un mouvement net
implicite, pas une distribution de probabilites discrete par reunion.

FedWatch differencie les prix de futures Fed Funds MOIS PAR MOIS (un contrat par echeance) pour
isoler chaque reunion individuellement. Verifie en direct le 2026-09-17 avant d'ecrire ce
fichier : l'acces gratuit a cette bande complete de contrats est ferme -- CME repond avec un
message explicite de blocage anti-scraping sur ses pages de settlements (Data Terms of Use), et
Yahoo Finance (deja utilise ailleurs dans ce depot) n'expose que le contrat CONTINU du mois le
plus proche (`ZQ=F`), pas les mois individuels au-dela (`ZQF26.CBT`, `ZQZ25.CBT`, etc. testes,
tous "Not Found").

Ce modele combine donc deux lectures, toutes deux 100% gratuites et officielles :

1. **Mois en cours (si une reunion y tombe)** : le prix du contrat Fed Funds front-month
   (`ZQ=F`) donne le taux moyen implicite du mois. Compare au taux effectif actuel (`DFF`,
   FRED) et pondere par le nombre de jours avant/apres la reunion dans le mois -- meme logique
   que FedWatch. C'est la lecture la plus precise disponible ici, mais elle ne dit RIEN les
   mois sans reunion (la majorite du temps : le FOMC se reunit ~8 fois par an).

2. **Fenetres a terme (0-1, 1-3, 3-6, 6-12 mois)** : taux forward implicites bootstrappes
   depuis la courbe des bons du Tresor US (`DGS1MO`, `DGS3MO`, `DGS6MO`, `DGS1`, FRED). Chaque
   fenetre donne un mouvement NET CUMULE implicite jusqu'a son echeance, PAS une probabilite
   isolee par reunion : avec seulement 4 points de courbe, impossible de separer les 2-3
   reunions qui tombent dans une meme fenetre les unes des autres. Le nombre de reunions FOMC
   contenues dans chaque fenetre est ecrit a cote de la lecture pour ne pas laisser croire a
   une precision qui n'existe pas.

Bootstrap de taux forward en approximation SIMPLE (pas de composition continue) -- justifie ici
par des maturites courtes (<=1 an) et des taux a un chiffre, ou l'ecart avec une formule composee
se compte en points de base, negligeable a cote de l'incertitude de marche elle-meme.
"""

import csv
import sys
from calendar import monthrange
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "chemin_taux_fed"
SEUIL_LECTURE_PB = 5  # en dessous, on lit "statu quo" plutot qu'un mouvement bruite


def lire_reunions_futures(reference: date | None = None) -> list:
    """Reunions FOMC dont la date de fin est aujourd'hui ou plus tard, triees."""
    chemin = BRUT / "fomc" / "calendrier.csv"
    if not chemin.exists():
        raise SerieVide(f"{chemin} n'existe pas")
    aujourdhui = reference or date.today()
    reunions = []
    with chemin.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            d_debut = date.fromisoformat(row["date_debut"])
            d_fin = date.fromisoformat(row["date_fin"])
            if d_fin >= aujourdhui:
                reunions.append((d_debut, d_fin))
    if not reunions:
        raise SerieVide("aucune reunion FOMC future dans le calendrier ingere")
    return sorted(reunions)


def lecture_mois_en_cours(dff: float, prochaine_reunion: date,
                          reference: date | None = None) -> dict | None:
    """Lecture precise via ZQ=F -- seulement si la prochaine reunion tombe dans le mois en
    cours (sinon le contrat front-month ne dit rien sur elle)."""
    aujourdhui = reference or date.today()
    if (prochaine_reunion.year, prochaine_reunion.month) != (aujourdhui.year, aujourdhui.month):
        return None
    try:
        zq = read_series(BRUT / "marches" / "taux_futures" / "FED_FUNDS_FRONT.csv", "close")
    except SerieVide:
        return None

    prix = zq[-1][1]
    taux_moyen_implicite = 100 - prix
    jours_dans_mois = monthrange(aujourdhui.year, aujourdhui.month)[1]
    jours_avant = prochaine_reunion.day
    jours_apres = jours_dans_mois - jours_avant
    if jours_apres <= 0:
        return None  # reunion sur les tout derniers jours du mois : pas assez de poids
                      # post-reunion dans la moyenne mensuelle pour en tirer une lecture fiable

    # taux_moyen_implicite = (jours_avant*dff + jours_apres*taux_apres) / jours_dans_mois
    taux_apres = (taux_moyen_implicite * jours_dans_mois - jours_avant * dff) / jours_apres
    return {
        "taux_implicite_pct": round(taux_moyen_implicite, 3),
        "mouvement_pb": round((taux_apres - dff) * 100, 1),
    }


def taux_forward(t1: float, y1: float, t2: float, y2: float) -> float:
    """Taux forward simple sur [t1,t2] (en annees), depuis deux taux spot y1,y2 (%)."""
    return (y2 * t2 - y1 * t1) / (t2 - t1)


def lecture(mouvement_pb: float) -> str:
    if mouvement_pb > SEUIL_LECTURE_PB:
        return "hausse"
    if mouvement_pb < -SEUIL_LECTURE_PB:
        return "baisse"
    return "statu quo"


def main() -> int:
    try:
        series = {
            "dff": read_series(BRUT / "fred" / "DFF.csv"),
            "dgs1mo": read_series(BRUT / "fred" / "DGS1MO.csv"),
            "dgs3mo": read_series(BRUT / "fred" / "DGS3MO.csv"),
            "dgs6mo": read_series(BRUT / "fred" / "DGS6MO.csv"),
            "dgs1an": read_series(BRUT / "fred" / "DGS1.csv"),
        }
        # Une sortie ne doit jamais paraitre plus fraiche que son entree la plus ancienne.
        # L'ancien code utilisait date.today(), meme lorsque les rendements s'arretaient plusieurs
        # jours plus tot, ce qui masquait precisement le probleme de fraicheur que la vue Fed doit
        # rendre visible.
        date_modele = min(serie[-1][0] for serie in series.values())
        aujourdhui = date.fromisoformat(date_modele)
        dff = series["dff"][-1][1]
        dgs1mo = series["dgs1mo"][-1][1]
        dgs3mo = series["dgs3mo"][-1][1]
        dgs6mo = series["dgs6mo"][-1][1]
        dgs1an = series["dgs1an"][-1][1]
        reunions = lire_reunions_futures(aujourdhui)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    prochaine_reunion = reunions[0][0]
    lignes = []

    court_terme = lecture_mois_en_cours(dff, prochaine_reunion, aujourdhui)
    if court_terme:
        lignes.append((
            aujourdhui.isoformat(), "mois_en_cours", prochaine_reunion.isoformat(), 1,
            court_terme["taux_implicite_pct"], court_terme["mouvement_pb"],
            lecture(court_terme["mouvement_pb"]), "futures_fed_funds_front",
            "moyenne", "contrat continu; estimation seulement si la reunion tombe ce mois",
        ))

    fenetres = [
        ("0-1 mois", 0.0, dff, 1 / 12, dgs1mo),
        ("1-3 mois", 1 / 12, dgs1mo, 3 / 12, dgs3mo),
        ("3-6 mois", 3 / 12, dgs3mo, 6 / 12, dgs6mo),
        ("6-12 mois", 6 / 12, dgs6mo, 1.0, dgs1an),
    ]
    for nom_fenetre, t1, y1, t2, y2 in fenetres:
        implicite = taux_forward(t1, y1, t2, y2)
        mouvement_pb = round((implicite - dff) * 100, 1)
        echeance = date.fromordinal(aujourdhui.toordinal() + round(t2 * 365))
        n_reunions = sum(1 for d_debut, _ in reunions if d_debut <= echeance)
        lignes.append((
            aujourdhui.isoformat(), nom_fenetre, echeance.isoformat(), n_reunions,
            round(implicite, 3), mouvement_pb, lecture(mouvement_pb),
            "forward_treasury_proxy", "faible",
            "mouvement net de fenetre; aucune probabilite isolee par reunion",
        ))

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "horizon", "echeance", "n_reunions_incluses",
         "taux_implicite_pct", "mouvement_implicite_pb", "lecture", "methode",
         "confiance", "limite"],
        lignes,
        key_columns=["date", "horizon"],
    )

    resume = " | ".join(
        f"{ligne[1]}: {ligne[5]:+.0f}pb ({ligne[6]}, confiance {ligne[8]})"
        for ligne in lignes
    )
    print(f"OK -- chemin de taux (pas des probabilites) : DFF={dff:.2f}%, "
          f"prochaine reunion {prochaine_reunion.isoformat()} "
          f"({len(reunions)} a venir dans le calendrier) -- {resume}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
