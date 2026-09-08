"""Modele -- regime monetaire et marche du travail, 5 blocs (US / Zone euro / Royaume-Uni /
Japon / Chine).

Volontairement PAS un quadrant croissance/inflation classique : l'inflation internationale
n'est pas disponible fraiche gratuitement (voir ingestion_fred.py pour le detail par pays,
teste et rejete pays par pays, pas suppose). Deux dimensions retenues parce qu'elles SONT
fraiches partout (ou presque) : le taux directeur (resserrement/assouplissement monetaire) et
le taux de chomage (tension/detente du marche du travail, absent pour la Chine -- aucune serie
fiable trouvee sur FRED).

Tendance mesuree sur ~6 mois calendaires (182 jours), pas sur un nombre de points fixe --
necessaire ici parce que les series melangent frequences quotidienne (DFF, ECBDFR, IUDSOIA) et
mensuelle (les 6 autres), contrairement au modele equivalent de global-macro-desk-cloud qui n'a
que des series homogenes.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import (BRUT, ETAT, SerieVide, accumuler_csv, latest, lire_historique,  # noqa: E402
                   nouvelle_figure, percentile_rang, read_series, sauvegarder_figure)

NOM_MODELE = "regime_monetaire_emploi"

SEUIL_TAUX_PT = 0.25     # un mouvement de banque centrale standard (25 pb)
SEUIL_CHOMAGE_PT = 0.30  # variation jugee significative pour un taux de chomage mensuel

# (bloc, serie_taux, serie_chomage_ou_None)
BLOCS = [
    ("US", "DFF", "UNRATE"),
    ("Zone euro", "ECBDFR", "LRHUTTTTDEM156S"),
    ("Royaume-Uni", "IUDSOIA", "LRHUTTTTGBM156S"),
    ("Japon", "IRSTCI01JPM156N", "LRHUTTTTJPM156S"),
    ("Chine", "IR3TIB01CNM156N", None),
]


def valeur_n_jours_avant(serie: list, n_jours: int) -> float:
    """Valeur a la date la plus proche de (derniere_date - n_jours), en remontant dans le passe
    -- marche indifferemment pour une frequence quotidienne ou mensuelle."""
    if len(serie) < 2:
        raise SerieVide("pas assez de points pour comparer a n jours avant")
    cible = date.fromisoformat(serie[-1][0]) - timedelta(days=n_jours)
    candidats = [v for d, v in serie if date.fromisoformat(d) <= cible]
    return candidats[-1] if candidats else serie[0][1]


def tendance(serie: list, seuil_pt: float, jours: int = 182) -> str:
    reference = valeur_n_jours_avant(serie, jours)
    ecart = latest(serie) - reference
    if ecart > seuil_pt:
        return "hausse"
    if ecart < -seuil_pt:
        return "baisse"
    return "stable"


def niveau_relatif(serie: list) -> str:
    """Tercile du niveau actuel dans tout l'historique disponible -- 'bas'/'moyen'/'haut'."""
    rang = percentile_rang(latest(serie), valeurs_de(serie))
    if rang >= 66.7:
        return "haut"
    if rang <= 33.3:
        return "bas"
    return "moyen"


def valeurs_de(serie: list) -> list:
    return [v for _, v in serie]


def tracer(chemin_csv) -> None:
    historique = lire_historique(chemin_csv)
    derniere_date = max(l["date"] for l in historique)
    lignes_du_jour = [l for l in historique if l["date"] == derniere_date]

    blocs = [l["bloc"] for l in lignes_du_jour]
    taux = [float(l["taux_dernier"]) for l in lignes_du_jour]
    couleurs = {"hausse": "#333333", "stable": "#999999", "baisse": "#cccccc"}
    barres_couleurs = [couleurs[l["taux_tendance"]] for l in lignes_du_jour]

    plt, fig, ax = nouvelle_figure(figsize=(8, 4.5))
    ax.barh(blocs, taux, color=barres_couleurs, edgecolor="black")
    for i, l in enumerate(lignes_du_jour):
        ax.text(float(l["taux_dernier"]) + 0.05, i,
                f"{float(l['taux_dernier']):.2f}% ({l['taux_tendance']})", va="center", fontsize=8)
    ax.set_xlabel("Taux directeur / proxy (%)")
    ax.set_title(f"Regime monetaire par bloc -- {derniere_date}")
    sauvegarder_figure(plt, fig, NOM_MODELE, "regime_monetaire_emploi")


def main() -> int:
    chemin_csv = ETAT / f"{NOM_MODELE}.csv"
    lignes = []
    echecs = []
    date_du_jour = None

    for bloc, id_taux, id_chomage in BLOCS:
        try:
            serie_taux = read_series(BRUT / "fred" / f"{id_taux}.csv")
        except SerieVide as e:
            echecs.append((bloc, str(e)))
            print(f"{bloc} : echec -- {e}")
            continue

        date_du_jour = date_du_jour or serie_taux[-1][0]
        tendance_taux = tendance(serie_taux, SEUIL_TAUX_PT)
        niveau_taux = niveau_relatif(serie_taux)

        if id_chomage is not None:
            try:
                serie_chomage = read_series(BRUT / "fred" / f"{id_chomage}.csv")
                tendance_chomage = tendance(serie_chomage, SEUIL_CHOMAGE_PT)
                chomage_dernier = latest(serie_chomage)
            except SerieVide as e:
                print(f"{bloc} : chomage indisponible -- {e}")
                tendance_chomage, chomage_dernier = "indisponible", ""
        else:
            tendance_chomage, chomage_dernier = "non_couvert", ""

        lignes.append([date_du_jour, bloc, latest(serie_taux), tendance_taux, niveau_taux,
                        chomage_dernier, tendance_chomage])
        print(f"{bloc} : taux {latest(serie_taux)}% ({tendance_taux}, niveau {niveau_taux}) "
              f"-- chomage {tendance_chomage}")

    if not lignes:
        print("echec -- aucun bloc exploitable")
        return 1

    accumuler_csv(
        chemin_csv,
        ["date", "bloc", "taux_dernier", "taux_tendance", "taux_niveau_relatif",
         "chomage_dernier", "chomage_tendance"],
        lignes,
    )
    tracer(chemin_csv)

    if echecs:
        print(f"\n{len(echecs)}/{len(BLOCS)} blocs en echec : {[b for b, _ in echecs]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
