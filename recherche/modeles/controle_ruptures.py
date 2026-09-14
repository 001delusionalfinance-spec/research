"""Controle des ruptures de perimetre dans les series accumulees.

**Le probleme, constate le 2026-09-14 lors d'un audit.** Beaucoup de modeles accumulent une
ligne par execution dans `recherche/etat/`. Quand l'univers de donnees change -- un contrat
ajoute, un historique rallonge -- la nouvelle ligne n'est plus comparable aux precedentes, et
rien ne le signale. Deux cas reels sur ce depot :

- `crowding_cross_asset` passe de "3 marches tendus sur 15" (20%) a "15 sur 32" (46,9%) d'une
  semaine a l'autre. Lu naivement, le marche se serait brutalement tendu. En realite l'univers
  du rapport de positionnement etait passe de 15 a 32 contrats.
- `walkforward_direction_sp500` passe de 470 a 7516 predictions quand l'historique du S&P est
  passe de 2 a 30 ans.

Aucun des deux n'etait une anomalie de marche. Les deux ressemblaient a une.

**Ce que fait ce controle.** Il surveille les colonnes qui decrivent la TAILLE de l'echantillon
(`n_marches`, `n_observations`, `n_total`...) et signale tout changement de palier durable.
Une taille d'echantillon qui change n'est jamais un resultat : c'est un changement de
perimetre, donc une rupture de comparabilite dans tout ce que la ligne contient par ailleurs.

Le controle ne corrige rien et ne supprime rien -- il rend la rupture VISIBLE, dans un fichier
et dans la lecture du jour. Effacer l'historique d'avant la rupture serait pire : on perdrait
la trace de ce qui a ete mesure, alors que ces mesures etaient justes dans leur perimetre.

Usage :
    python controle_ruptures.py
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ETAT  # noqa: E402

SORTIE = ETAT / "ruptures_perimetre.csv"
# Une colonne decrit la taille de l'echantillon si son nom COMMENCE par n_ / nombre_, ou se
# termine par _total.
#
# Premiere version fautive, corrigee au test du 2026-09-14 : elle cherchait "n_" n'importe ou
# dans le nom. Or "variatio(n_)vix", "correlatio(n_)momentum" et "importance_variatio(n_)vix"
# contiennent tous cette sequence sans etre des tailles d'echantillon -- huit faux positifs, et
# aucune des deux vraies ruptures. Un controle qui crie faux huit fois est desactive aussitot.
PREFIXES_TAILLE = ("n_", "nombre_")
SUFFIXES_TAILLE = ("_total",)
SEUIL_RUPTURE_PCT = 20.0   # variation de palier en deca de laquelle on ne signale pas
# Deux lignes suffisent : une rupture peut survenir des la deuxieme execution, et c'est
# exactement le cas des deux ruptures reelles de ce depot, que MIN_LIGNES=3 excluait.
MIN_LIGNES = 2


def _nombre(texte):
    try:
        return float(str(texte).strip())
    except (TypeError, ValueError):
        return None


def _denominateurs(lignes: list, colonnes: list) -> set:
    """Parmi les colonnes de comptage, celles qui jouent le role de DENOMINATEUR.

    Distinction necessaire, constatee au test : toutes les colonnes en n_ ne decrivent pas la
    taille de l'echantillon. Dans `crowding_cross_asset`, `n_marches_total` est l'univers
    (denominateur) alors que `n_marches_tendus` est un RESULTAT -- le nombre de marches qui
    remplissent une condition. Le premier qui change est une rupture de perimetre ; le second
    qui change est justement ce que le modele est cense mesurer. Les confondre ferait crier le
    controle a chaque variation normale.

    Regle : une colonne est un denominateur si son nom se termine par _total, ou si elle est la
    plus grande colonne de comptage de sa ligne (un total majore par construction ses parties).
    """
    trouves = {c for c in colonnes if c.lower().endswith(SUFFIXES_TAILLE)}
    for ligne in lignes:
        valeurs = {c: _nombre(ligne.get(c)) for c in colonnes}
        valeurs = {c: v for c, v in valeurs.items() if v is not None}
        if len(valeurs) > 1:
            trouves.add(max(valeurs, key=valeurs.get))
    return trouves


def _colonnes_de_taille(entete: list) -> list:
    retenues = []
    for colonne in entete:
        if not colonne:
            continue
        nom = colonne.lower()
        if nom.startswith(PREFIXES_TAILLE) or nom.endswith(SUFFIXES_TAILLE):
            retenues.append(colonne)
    return retenues


def analyser(chemin: Path) -> list:
    """Retourne les ruptures trouvees dans un fichier d'etat accumule."""
    try:
        with chemin.open(encoding="utf-8", newline="") as f:
            lignes = list(csv.DictReader(f))
    except OSError:
        return []
    if len(lignes) < MIN_LIGNES or "date" not in (lignes[0] or {}):
        return []

    colonnes = _colonnes_de_taille(list(lignes[0]))
    denominateurs = _denominateurs(lignes, colonnes)

    ruptures = []
    for colonne in colonnes:
        # Une seule valeur par date : si le fichier a plusieurs lignes par date (sortie
        # transversale), la notion de palier n'a pas de sens et on passe.
        par_date = {}
        for ligne in lignes:
            valeur = _nombre(ligne.get(colonne))
            if valeur is None:
                continue
            par_date.setdefault(ligne["date"], []).append(valeur)
        if not par_date or any(len(v) > 1 for v in par_date.values()):
            continue

        suite = [(d, v[0]) for d, v in sorted(par_date.items())]
        for (date_avant, avant), (date_apres, apres) in zip(suite, suite[1:]):
            if avant <= 0:
                continue
            variation = abs(apres - avant) / avant * 100
            if variation >= SEUIL_RUPTURE_PCT:
                ruptures.append({
                    "serie": chemin.stem, "colonne": colonne,
                    "date_avant": date_avant, "taille_avant": avant,
                    "date_apres": date_apres, "taille_apres": apres,
                    "variation_pct": round(variation, 1),
                    "nature": ("perimetre" if colonne in denominateurs
                               else "a verifier (peut etre un resultat)"),
                })
    return ruptures


def main() -> int:
    fichiers = sorted(ETAT.glob("*.csv"))
    if not fichiers:
        print(f"echec -- aucun fichier d'etat dans {ETAT}")
        return 1

    ruptures = []
    for chemin in fichiers:
        if chemin.name in (SORTIE.name, "fraicheur.csv"):
            continue
        ruptures.extend(analyser(chemin))

    if ruptures:
        SORTIE.parent.mkdir(parents=True, exist_ok=True)
        with SORTIE.open("w", newline="", encoding="utf-8") as f:
            ecrivain = csv.DictWriter(f, fieldnames=list(ruptures[0]))
            ecrivain.writeheader()
            ecrivain.writerows(ruptures)

    if not ruptures:
        print(f"OK -- {len(fichiers)} sorties controlees, aucune rupture de perimetre detectee")
        return 0

    perimetre = [r for r in ruptures if r["nature"] == "perimetre"]
    autres = [r for r in ruptures if r["nature"] != "perimetre"]
    if not perimetre:
        print(f"OK -- aucune rupture de perimetre. {len(autres)} variation(s) de comptage "
              f"signalee(s) pour verification, qui sont probablement des resultats.")
        return 0

    series_touchees = sorted({r["serie"] for r in perimetre})
    print(f"OK -- {len(perimetre)} rupture(s) de PERIMETRE sur {len(series_touchees)} serie(s) : "
          f"les lignes d'avant et d'apres ne sont PAS comparables entre elles")
    for r in perimetre:
        print(f"   {r['serie']} / {r['colonne']} : {r['taille_avant']:.0f} le "
              f"{r['date_avant']} -> {r['taille_apres']:.0f} le {r['date_apres']} "
              f"({r['variation_pct']:+.0f}%) -- tout ce que cette ligne contient par ailleurs "
              f"a change d'echelle en meme temps")
    if autres:
        print(f"   ({len(autres)} autre(s) variation(s) de comptage listee(s) dans "
              f"{SORTIE.name}, probablement des resultats et non des ruptures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
