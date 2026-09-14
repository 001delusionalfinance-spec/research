"""Modele -- le differentiel de taux explique-t-il le change ?

Pour chaque paire du G10, met en regard le differentiel de taux 2 ans entre les deux blocs et le
cours de change, et mesure la correlation de leurs variations mensuelles.

**Pourquoi ce modele existe.** La theorie dit qu'une devise dont les taux montent plus vite que
ceux d'en face doit s'apprecier. En pratique ce lien se rompt regulierement -- quand le marche
price un risque de credit souverain, une intervention, ou une fuite vers la qualite. Mesurer la
correlation plutot que la supposer permet de voir QUAND le lien tient, et donc quand une vue de
change fondee sur les taux a une chance d'etre juste.

**Garde-fou multiple-testing.** On teste plusieurs paires d'un coup ; sur huit tests
independants, en trouver un "significatif a 5%" par hasard est l'issue la plus probable. La
correction de Bonferroni est donc appliquee, et c'est elle qui fait foi -- pas la p-valeur brute.
La convention de cotation est respectee : pour une paire cotee USD/XXX (yen, franc, couronnes),
une hausse du cours est une hausse du dollar, donc le differentiel est pris dans l'autre sens.
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import (BRUT, ETAT, SerieVide, correlation_avec_p_valeur,  # noqa: E402
                  ecrire_csv, read_series, seuils_bonferroni)

NOM_MODELE = "differentiel_taux_change"
SOUV = BRUT / "souverains"
FX = BRUT / "marches" / "fx"

# (paire, taux de la devise de BASE, taux de la devise de CONTREPARTIE)
# Le differentiel est toujours base - contrepartie : il monte quand la devise de base doit
# s'apprecier selon la theorie.
PAIRES = [
    ("EURUSD", (SOUV / "ZONE_EURO_AAA_2A.csv", "taux"), (BRUT / "fred" / "DGS2.csv", "value")),
    ("USDJPY", (BRUT / "fred" / "DGS2.csv", "value"), (SOUV / "JAPON_2A.csv", "taux")),
    ("GBPUSD", (SOUV / "UK_5A.csv", "taux"), (BRUT / "fred" / "DGS5.csv", "value")),
    ("USDCAD", (BRUT / "fred" / "DGS2.csv", "value"), (SOUV / "CANADA_2A.csv", "taux")),
    ("AUDUSD", (SOUV / "AUSTRALIE_2A.csv", "taux"), (BRUT / "fred" / "DGS2.csv", "value")),
    ("USDSEK", (BRUT / "fred" / "DGS2.csv", "value"), (SOUV / "SUEDE_2A.csv", "taux")),
    ("EURJPY", (SOUV / "ZONE_EURO_AAA_2A.csv", "taux"), (SOUV / "JAPON_2A.csv", "taux")),
    ("EURGBP", (SOUV / "ZONE_EURO_AAA_5A.csv", "taux"), (SOUV / "UK_5A.csv", "taux")),
]
PAS_JOURS = 21   # variations mensuelles : le lien taux/change ne se lit pas au jour le jour
MIN_POINTS = 24


def variations(valeurs: list, pas: int) -> list:
    """Variations sur `pas` observations, en fenetres DISJOINTES.

    Defaut reel trouve au premier test du 2026-09-14 : une premiere version calculait des
    variations glissantes (chaque jour comparé au jour a J-21). Ces fenetres se chevauchent a
    95%, donc les observations produites ne sont pas independantes -- elles partagent presque
    toute leur information. Le nombre d'observations passe alors pour etre de plusieurs
    milliers alors qu'il n'y a qu'une centaine de mois reellement distincts, et la p-valeur du
    test de correlation s'ecrase mecaniquement. Resultat : les HUIT paires ressortaient
    significatives, y compris apres Bonferroni -- un resultat trop beau qui ne mesurait que la
    redondance de la fenetre glissante.

    En prenant un point tous les `pas`, les variations ne se recouvrent plus.
    """
    echantillon = valeurs[::pas]
    return [b - a for a, b in zip(echantillon, echantillon[1:])]


def main() -> int:
    resultats, echecs = [], []
    for nom, (p_base, c_base), (p_contre, c_contre) in PAIRES:
        try:
            base = dict(read_series(p_base, c_base))
            contre = dict(read_series(p_contre, c_contre))
            change = dict(read_series(FX / f"{nom}.csv", "close"))
            communes = sorted(set(base) & set(contre) & set(change))
            if len(communes) < MIN_POINTS + PAS_JOURS:
                raise SerieVide(f"seulement {len(communes)} dates communes")

            differentiel = [base[d] - contre[d] for d in communes]
            cours = [change[d] for d in communes]
            var_diff = variations(differentiel, PAS_JOURS)
            var_cours = variations(cours, PAS_JOURS)
            r, p = correlation_avec_p_valeur(var_diff, var_cours)
            resultats.append([nom, communes[-1], round(differentiel[-1], 3), round(r, 3),
                              round(p, 5), len(var_diff)])
        except (SerieVide, ValueError, ZeroDivisionError) as e:
            echecs.append((nom, str(e)))

    if not resultats:
        print(f"echec -- aucune paire exploitable ({len(echecs)} en erreur)")
        return 1

    significatifs = seuils_bonferroni([r[4] for r in resultats])
    for ligne, sig in zip(resultats, significatifs):
        ligne.append("oui" if sig else "non")

    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["paire", "date", "differentiel_taux_pt", "correlation", "p_valeur",
                "n_observations", "significatif_apres_bonferroni"], resultats)

    tiennent = [r[0] for r in resultats if r[6] == "oui" and r[3] > 0]
    contraires = [r[0] for r in resultats if r[6] == "oui" and r[3] < 0]
    if tiennent:
        lecture = (f"le lien taux/change tient sur {len(tiennent)} paire(s) apres correction "
                   f"pour tests multiples : {', '.join(tiennent)}")
    else:
        lecture = ("aucune paire ne montre de lien taux/change significatif apres correction "
                   "-- le change est actuellement conduit par autre chose que le differentiel")
    if contraires:
        lecture += (f". Lien INVERSE et significatif sur {', '.join(contraires)} : la devise "
                    f"se deprecie quand son differentiel monte, configuration typique d'une "
                    f"prime de risque ou d'une fuite vers la qualite")

    print(f"OK -- {len(resultats)} paires testees sur variations a {PAS_JOURS} jours -- {lecture}")
    if echecs:
        print(f"   {len(echecs)} paire(s) non exploitable(s) : {[n for n, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
