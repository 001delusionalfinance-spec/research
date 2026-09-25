"""Controle de fraicheur -- detecte les series qui se sont figees, avant que les modeles ne
continuent a calculer dessus en silence.

**Le probleme reel qu'il resout.** Les ingestions ecrasent leur fichier a chaque passage. Si
une source cesse d'alimenter une serie, le fichier reste en place avec sa derniere valeur : ni
erreur, ni fichier vide, rien. Les modeles continuent a tourner, produisent des sorties
d'apparence normale, et personne ne voit que l'entree est morte. Ce n'est pas une hypothese --
sur ce depot, six series au moins ont ete trouvees gelees en les testant a la main : les
proxies de taux Suisse (2024-03), Nouvelle-Zelande (2024-12) et Suede (2020-10), les CPI
internationaux de l'OCDE (jusqu'a 2021-06), la serie de compte courant BOPBCA (2014-01), et une
serie du bilan canadien (2022-12).

**Pourquoi le seuil est DEDUIT et non configure.** Le reflexe naturel est d'ecrire un seuil par
serie. Il a ete essaye et il rate : le 2026-09-14, cinq seuils poses a la main se sont reveles
faux le jour meme, chaque fois parce qu'ils ignoraient le rythme de publication propre a la
serie -- CPI trimestriel australien et neo-zelandais rejetes a 105 jours, taux directeur coreen
a 17 jours, ratio de service de la dette du BIS ou les douze pays sont alignes sur le meme
trimestre, production industrielle de la zone euro qui parait apres celle de ses membres. Un
catalogue de seuils ecrit a la main pour des centaines de series serait faux le jour de son
ecriture, et personne ne le maintiendrait.

Ici le rythme est **mesure sur la serie elle-meme** : l'ecart median entre deux observations
consecutives dit si elle est quotidienne, hebdomadaire, mensuelle ou trimestrielle. Le seuil
en decoule. Deux exceptions documentees portent sur la cadence de LIVRAISON, impossible a
deduire des observations : le MOF livre ses points JGB quotidiens par lot mensuel et le BIS
alimente le taux coreen avec davantage de retard que ses autres taux. Le controle reprend les
memes tolerances que leurs scripts d'ingestion afin de ne pas appeler "suspecte" une source que
l'ingestion vient de valider.

Sortie : `recherche/etat/fraicheur.csv` (une ligne par serie) et un resume lisible. Le code de
retour vaut 1 si au moins une serie est classee GELEE : c'est le signal d'alerte, il fait
passer le workflow au rouge. Une serie seulement SUSPECTE ne fait pas echouer -- sinon
l'alerte crierait en permanence et serait desactivee au bout d'une semaine.

Usage :
    python controle_fraicheur.py
"""

import csv
import statistics
import sys
from datetime import date, datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
BRUT_DIR = RACINE / "donnees" / "brut"
SORTIE = RACINE / "recherche" / "etat" / "fraicheur.csv"

# Multiples de l'ecart median de la serie. CALIBRES CONTRE LES GELS REELLEMENT OBSERVES sur ce
# depot, pas choisis a vue -- c'est la seule facon d'obtenir une alerte qu'on ne finira pas par
# ignorer.
#
# Cotes gels averes, exprimes en multiples du rythme de la serie :
#   proxy de taux Suisse (2024-03)        ~30x     proxy Nouvelle-Zelande (2024-12)  ~20x
#   proxy Suede (2020-10)                 ~70x     CPI OCDE (jusqu'a 2021-06)        ~60x
#   compte courant BOPBCA (2014-01)      ~150x     bilan canadien V36632 (2022-12)   ~45x
# Cote series VIVANTES mais publiees avec retard : les mensuelles de source OCDE tournent
# autour de 3,4x leur rythme, c'est leur regime normal de publication.
#
# Un premier reglage a 3x / 6x a ete essaye le 2026-09-14 : il signalait 23 series d'un coup,
# toutes vivantes. Une alerte qui crie tous les jours est desactivee en une semaine, donc elle
# ne protege rien. Portes a 5x / 9x : aucun faux positif sur l'etat du jour, et les six gels
# reels ci-dessus auraient tous ete attrapes, le plus discret avec plus du double de marge.
FACTEUR_SUSPECT = 5.0
FACTEUR_GELE = 9.0
# Plancher : pour une serie quotidienne (ecart median de 1 jour), 6 x 1 jour declencherait au
# moindre pont. Aucun signalement en dessous de cette anciennete, quel que soit le rythme.
PLANCHER_JOURS = 21
MIN_OBSERVATIONS = 8

# Planchers lies a la cadence de livraison de la source, et non a celle des observations.
# Ils sont alignes sur RETARD_MAX_MOF et RETARD_MAX_TAUX d'ingestion_souverains_quotidiens.py
# et ingestion_bis_macro.py. Sans cela, des observations quotidiennes livrees mensuellement
# sont faussement classees suspectes apres 21 jours.
RETARDS_SOURCE = {
    "bis/taux_directeurs/KR.csv": (35, 70),
}

FORMATS_DATE = ("%Y-%m-%d", "%Y-%m", "%d %b %Y", "%d-%b-%Y", "%Y/%m/%d")


def _lire_date(brut: str):
    """Renvoie une date, ou None. Gere aussi les periodes trimestrielles ('2026-Q1')."""
    brut = brut.strip().strip('"')
    if not brut:
        return None
    if "-Q" in brut:
        try:
            annee, trimestre = brut.split("-Q")
            return date(int(annee), (int(trimestre) - 1) * 3 + 1, 1)
        except (ValueError, IndexError):
            return None
    for motif in FORMATS_DATE:
        try:
            return datetime.strptime(brut, motif).date()
        except ValueError:
            continue
    return None


def _dates_du_fichier(chemin: Path) -> list:
    """Dates de la premiere colonne. Liste vide si le fichier n'est pas une serie temporelle."""
    try:
        with chemin.open(encoding="utf-8", errors="replace", newline="") as f:
            lignes = list(csv.reader(f))
    except OSError:
        return []
    if len(lignes) < 2:
        return []

    # Certaines sources ecrivent en point-virgule ; on retente si la premiere colonne d'une
    # ligne de donnees contient encore un separateur.
    if len(lignes[1]) == 1 and ";" in lignes[1][0]:
        lignes = [ligne[0].split(";") for ligne in lignes if ligne]

    dates, echecs = [], 0
    for ligne in lignes[1:]:
        if not ligne:
            continue
        jour = _lire_date(ligne[0])
        if jour is None:
            echecs += 1
        else:
            dates.append(jour)
    total = len(dates) + echecs
    # Un fichier d'index (libelles, urls) n'a pas de dates : on l'ecarte au lieu de le signaler.
    if total == 0 or len(dates) / total < 0.8:
        return []
    return sorted(set(dates))


def analyser(chemin: Path) -> dict | None:
    dates = _dates_du_fichier(chemin)
    if len(dates) < MIN_OBSERVATIONS:
        return None

    ecarts = [(b - a).days for a, b in zip(dates, dates[1:]) if (b - a).days > 0]
    if not ecarts:
        return None
    rythme = statistics.median(ecarts)

    anciennete = (datetime.now(timezone.utc).date() - dates[-1]).days
    seuil_suspect = max(rythme * FACTEUR_SUSPECT, PLANCHER_JOURS)
    seuil_gele = max(rythme * FACTEUR_GELE, PLANCHER_JOURS * 2)
    relatif = str(chemin.relative_to(BRUT_DIR)).replace("\\", "/")
    retard_source = RETARDS_SOURCE.get(relatif)
    if relatif.startswith("souverains/JAPON_"):
        retard_source = (45, 90)
    if retard_source:
        seuil_suspect = max(seuil_suspect, retard_source[0])
        seuil_gele = max(seuil_gele, retard_source[1])

    if anciennete >= seuil_gele:
        verdict = "GELEE"
    elif anciennete >= seuil_suspect:
        verdict = "SUSPECTE"
    else:
        verdict = "OK"

    return {
        "serie": relatif,
        "derniere_observation": dates[-1].isoformat(),
        "anciennete_jours": anciennete,
        "rythme_median_jours": round(rythme, 1),
        "seuil_gele_jours": round(seuil_gele, 1),
        "n_observations": len(dates),
        "verdict": verdict,
    }


def main() -> int:
    if not BRUT_DIR.exists():
        print("Aucun dossier de donnees brutes -- rien a controler.")
        return 0

    resultats = [r for r in (analyser(c) for c in sorted(BRUT_DIR.rglob("*.csv"))) if r]
    if not resultats:
        print("Aucune serie temporelle exploitable trouvee.")
        return 0

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(resultats[0]))
        ecrivain.writeheader()
        ecrivain.writerows(sorted(resultats, key=lambda r: -r["anciennete_jours"]))

    gelees = [r for r in resultats if r["verdict"] == "GELEE"]
    suspectes = [r for r in resultats if r["verdict"] == "SUSPECTE"]

    print(f"{len(resultats)} series controlees -> {SORTIE}")
    print(f"  {len(resultats) - len(gelees) - len(suspectes)} a jour, "
          f"{len(suspectes)} suspectes, {len(gelees)} gelees")

    for r in suspectes:
        print(f"  SUSPECTE  {r['serie']} : derniere observation {r['derniere_observation']}, "
              f"{r['anciennete_jours']} jours, pour un rythme habituel de "
              f"{r['rythme_median_jours']} jours")
    for r in gelees:
        print(f"  GELEE     {r['serie']} : derniere observation {r['derniere_observation']}, "
              f"{r['anciennete_jours']} jours, pour un rythme habituel de "
              f"{r['rythme_median_jours']} jours -- la source a probablement cesse d'alimenter "
              f"cette serie, les modeles qui la lisent travaillent sur une valeur morte")

    if gelees:
        print(f"\n{len(gelees)} serie(s) gelee(s) : echec volontaire pour faire remonter "
              f"l'alerte.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
