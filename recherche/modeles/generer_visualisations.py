"""Genere uniquement les graphiques qui ajoutent une information visuelle.

Le CSV est la sortie normale d'un modele. Un graphique n'est produit que lorsqu'une evolution
temporelle ou une comparaison entre entites est plus rapide a comprendre visuellement. La
selection ci-dessous est explicite : elle evite les apercus automatiques, souvent redondants ou
trompeurs, qui existaient auparavant.

Les figures propres a certains modeles (COT, correlation glissante, regime monetaire et EWMA)
restent generees par ces modeles. Ce script gere seulement les graphiques communs selectionnes.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ETAT, VISUALISATIONS, nouvelle_figure, sauvegarder_figure  # noqa: E402

MAX_SERIES_TRACEES = 6
MAX_BARRES = 20
MIN_POINTS_SERIE = 3

# Chaque graphique doit repondre a une question de lecture identifiable. Les sorties absentes
# de cette liste restent accessibles sous forme de CSV, sans image decorative.
CONFIG_GRAPHIQUES = {
    "conditions_financieres": {
        "mode": "serie", "colonnes": ["indice_composite"],
    },
    "courbe_taux_us": {
        "mode": "serie", "colonnes": ["taux_10ans", "taux_2ans", "spread_pt"],
    },
    "liquidite_nette_fed": {
        "mode": "serie", "colonnes": ["liquidite_nette_musd"],
    },
    "regle_taylor": {
        "mode": "serie", "colonnes": ["taux_recommande_taylor_pct", "taux_fed_reel_pct"],
    },
    "taux_reel_us": {
        "mode": "serie", "colonnes": ["taux_nominal_pct", "inflation_yoy_pct", "taux_reel_pct"],
    },
    "matieres_premieres_macro": {
        "mode": "serie",
        "colonnes": ["variation_ratio_3m_pct", "variation_brent_3m_pct", "variation_gaz_3m_pct"],
    },
    "facteur_qualite_credit": {
        "mode": "serie", "colonnes": ["spread_hy", "spread_ig"],
    },
    "crowding_cross_asset": {
        "mode": "serie", "colonnes": ["pct_tendus"],
    },
    "var_drawdown": {
        "mode": "serie", "colonnes": ["var_95_pct", "cvar_95_pct", "drawdown_max_252j_pct"],
    },
    "garch": {
        "mode": "serie", "colonnes": ["vol_garch_annualisee"],
    },
    "ornstein_uhlenbeck_vix": {
        "mode": "serie", "colonnes": ["vix_actuel", "mu_niveau_moyen"],
    },
    "hp_filter_taux": {
        "mode": "serie", "colonnes": ["taux_10ans_observe", "tendance_hp"],
    },
    "decomposition_stl": {
        "mode": "serie", "colonnes": ["tendance", "composante_saisonniere", "residu"],
    },
    "bilans_banques_centrales": {
        "mode": "comparaison", "etiquette": "bilan", "colonnes": ["variation_12m_pct"],
    },
    "inflation_comparee": {
        "mode": "comparaison", "etiquette": "bloc", "colonnes": ["inflation_annuelle_pct"],
    },
    "pentes_courbes": {
        "mode": "comparaison", "etiquette": "bloc", "colonnes": ["pente_pt"],
    },
    "indices_mondiaux": {
        "mode": "comparaison", "etiquette": "indice", "colonnes": ["variation_12m_pct"],
    },
    "rotation_sectorielle": {
        "mode": "comparaison", "etiquette": "secteur", "colonnes": ["rendement_3m_pct"],
    },
    "vol_cross_asset": {
        "mode": "comparaison", "etiquette": "mesure", "colonnes": ["percentile_5_ans"],
    },
    "stress_test_historique": {
        "mode": "comparaison", "etiquette": "scenario", "colonnes": ["chute_pct"],
    },
    "positionnement_devises": {
        "mode": "comparaison", "etiquette": "devise", "colonnes": ["percentile_historique"],
    },
    "positionnement_courbe_taux": {
        "mode": "comparaison", "etiquette": "maturite", "colonnes": ["percentile_historique"],
    },
}


def _nombre(texte):
    try:
        return float(str(texte).strip())
    except (TypeError, ValueError):
        return None


def _lire(chemin: Path):
    with chemin.open(encoding="utf-8", newline="") as flux:
        lignes = list(csv.reader(flux))
    if len(lignes) < 2:
        raise ValueError("fichier vide ou sans donnees")
    return lignes[0], lignes[1:]


def _indices(entete: list[str], noms: list[str]) -> list[int]:
    absentes = [nom for nom in noms if nom not in entete]
    if absentes:
        raise ValueError(f"colonnes absentes: {absentes}")
    return [entete.index(nom) for nom in noms]


def _tracer_serie(nom: str, entete: list, donnees: list, colonnes: list[int]) -> Path:
    if "date" not in entete:
        raise ValueError("colonne date absente")
    index_date = entete.index("date")
    plt, fig, ax = nouvelle_figure(figsize=(10, 5))
    tracees = 0
    for index in colonnes[:MAX_SERIES_TRACEES]:
        points = [
            (ligne[index_date], _nombre(ligne[index]))
            for ligne in donnees
            if max(index_date, index) < len(ligne)
        ]
        points = [(date, valeur) for date, valeur in points if valeur is not None]
        if len(points) < MIN_POINTS_SERIE:
            continue
        ax.plot(
            [date for date, _ in points], [valeur for _, valeur in points],
            label=entete[index], linewidth=1.2,
        )
        tracees += 1
    if not tracees:
        raise ValueError("pas assez de points numeriques")
    ax.set_title(nom.replace("_", " "))
    ax.tick_params(axis="x", rotation=45, labelsize=7)
    etiquettes = ax.get_xticks()
    if len(etiquettes) > 12:
        ax.set_xticks(etiquettes[:: max(1, len(etiquettes) // 10)])
    if tracees > 1:
        ax.legend(fontsize=7)
    return sauvegarder_figure(plt, fig, nom, "apercu")


def _tracer_comparaison(
    nom: str, entete: list, donnees: list, colonne: int, index_etiquette: int,
) -> Path:
    # Les historiques peuvent contenir plusieurs dates par entite. La derniere occurrence est
    # l'etat courant et remplace les precedentes dans la photographie comparative.
    dernieres = {}
    for ligne in donnees:
        if max(colonne, index_etiquette) >= len(ligne):
            continue
        valeur = _nombre(ligne[colonne])
        etiquette = ligne[index_etiquette].strip()
        if etiquette and valeur is not None:
            dernieres[etiquette] = valeur
    paires = sorted(dernieres.items(), key=lambda paire: paire[1])[-MAX_BARRES:]
    if not paires:
        raise ValueError("aucune valeur numerique a tracer")
    plt, fig, ax = nouvelle_figure(figsize=(9, max(3, 0.35 * len(paires) + 1)))
    ax.barh(
        [etiquette for etiquette, _ in paires], [valeur for _, valeur in paires],
        color=["#b02418" if valeur < 0 else "#1f5f8b" for _, valeur in paires],
    )
    ax.set_title(f"{nom.replace('_', ' ')} -- {entete[colonne]}")
    ax.tick_params(axis="y", labelsize=8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    return sauvegarder_figure(plt, fig, nom, "apercu")


def _nettoyer_apercus_non_selectionnes() -> int:
    supprimes = 0
    for chemin in VISUALISATIONS.glob("*/apercu.png"):
        if chemin.parent.name not in CONFIG_GRAPHIQUES:
            chemin.unlink()
            supprimes += 1
    for dossier in sorted(VISUALISATIONS.glob("*"), reverse=True):
        if dossier.is_dir() and not any(dossier.iterdir()):
            dossier.rmdir()
    return supprimes


def main() -> int:
    VISUALISATIONS.mkdir(parents=True, exist_ok=True)
    supprimes = _nettoyer_apercus_non_selectionnes()
    generes, erreurs = 0, []
    for nom, config in CONFIG_GRAPHIQUES.items():
        chemin = ETAT / f"{nom}.csv"
        try:
            entete, donnees = _lire(chemin)
            colonnes = _indices(entete, config["colonnes"])
            if config["mode"] == "serie":
                _tracer_serie(nom, entete, donnees, colonnes)
            else:
                index_etiquette = _indices(entete, [config["etiquette"]])[0]
                _tracer_comparaison(nom, entete, donnees, colonnes[0], index_etiquette)
            generes += 1
        except (OSError, ValueError, IndexError) as erreur:
            erreurs.append(f"{nom}: {erreur}")

    modeles_avec_graphique = {
        chemin.parent.name for chemin in VISUALISATIONS.rglob("*.png")
    }
    n_csv_seuls = sum(
        1 for chemin in ETAT.glob("*.csv") if chemin.stem not in modeles_avec_graphique
    )
    print(
        f"OK -- {generes} graphiques selectionnes, {n_csv_seuls} sorties conservees en CSV "
        f"seul, {supprimes} anciens apercus supprimes"
    )
    if erreurs:
        print("Echecs de generation : " + "; ".join(erreurs))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
