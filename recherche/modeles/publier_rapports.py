"""Publie toutes les sorties de recherche dans un point d'entree unique.

Les scripts restent ranges par implementation dans ``recherche/``. Leurs sorties vivent
directement dans ``rapports/`` : ce module construit la synthese thematique, les rapports par
sujet et l'etat de qualite sans copier les CSV ni les graphiques.

Usage :
    python recherche/modeles/publier_rapports.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib import ETAT, REPO_ROOT, VISUALISATIONS  # noqa: E402
from run_all_modeles import MODELES  # noqa: E402

RAPPORTS = REPO_ROOT / "rapports"
DONNEES_PUBLIEES = ETAT
GRAPHIQUES_PUBLIES = VISUALISATIONS
THEMES_DIR = RAPPORTS / "themes"


THEMES = {
    "banques-centrales": {
        "titre": "Banques centrales et politique monetaire",
        "description": (
            "Decisions, fonctions de reaction, bilan, communication et trajectoires de taux."
        ),
        "modeles": {
            "regime_monetaire_emploi", "regle_taylor", "chemin_taux_fed",
            "divergence_taux_directeurs", "bilans_banques_centrales",
            "liquidite_nette_fed", "ton_banques_centrales", "ton_fomc",
            "frequence_mots_cles_fomc", "complexite_texte_fomc", "ton_minutes_fomc",
            "ecart_communique_minutes", "complexite_texte_minutes",
            "entites_geographiques_minutes", "similarite_vocabulaire_minutes",
            "lisibilite_flesch_kincaid", "frequence_mots_cles_minutes",
            "langage_prudence", "intensite_desaccord",
        },
    },
    "cycle-macro": {
        "titre": "Croissance, inflation et cycle macro",
        "description": (
            "Activite, emploi, inflation, immobilier, commerce et finances publiques."
        ),
        "modeles": {
            "sahm_rule", "cycle_immobilier", "inflation_comparee", "activite_zone_euro",
            "soutenabilite_dette", "matieres_premieres_macro", "surprise_macro_composite",
            "balance_commerciale", "surprise_inflation",
        },
    },
    "taux-credit-liquidite": {
        "titre": "Taux, credit et liquidite",
        "description": (
            "Courbes souveraines, conditions financieres, credit, emission et taux reels."
        ),
        "modeles": {
            "taux_reel_us", "courbe_taux_us", "cycle_credit", "conditions_financieres",
            "emission_tresor_us", "pentes_courbes", "stationnarite_taux",
            "cointegration_taux", "pca_taux", "hp_filter_taux",
            "facteur_qualite_credit", "momentum_credit", "ornstein_uhlenbeck_credit",
        },
    },
    "marches-allocation": {
        "titre": "Marches, facteurs et allocation",
        "description": (
            "Change, actions, secteurs, facteurs, rotations et signaux d'allocation."
        ),
        "modeles": {
            "reer_us", "differentiel_taux_change", "indices_mondiaux",
            "correlation_glissante", "clustering_marches", "beta_facteur_macro",
            "momentum_prix", "carry_proxy", "beta_vol", "rotation_sectorielle",
            "saisonnalite", "dispersion_sectorielle", "low_volatility",
            "momentum_cross_sectional", "cointegration_secteurs", "correlation_facteurs",
        },
    },
    "positionnement": {
        "titre": "Positionnement et comportement",
        "description": (
            "COT, crowding, devises, courbe, extremes et divergences entre prix et positions."
        ),
        "modeles": {
            "positionnement_courbe_taux", "positionnement_devises", "positionnement_cot",
            "momentum_positionnement", "crowding_cross_asset", "divergence_cot_prix",
            "ratio_commercial_speculatif", "rotation_risk_on_off",
            "concentration_traders", "metaux_precieux", "persistance_extremes",
            "correlations_positionnement", "dollar_smile", "extremes_historiques",
            "correlation_cot_prix",
        },
    },
    "risques-regimes": {
        "titre": "Risques, volatilite et regimes",
        "description": (
            "Volatilite, queues, drawdowns, stress, contagion et changements de regime."
        ),
        "modeles": {
            "vol_cross_asset", "volatilite_ewma", "garch", "hurst",
            "ornstein_uhlenbeck_vix", "changepoint_volatilite", "kalman_niveau_local",
            "var_sp500_vix", "analyse_spectrale", "var_drawdown", "skew_kurtosis",
            "ratios_performance", "covar", "stress_test_historique", "sizing_robuste",
            "nombre_effectif_paris", "detection_saut", "choc_taux",
            "qualite_regime_macro", "var_conditionnelle_regime",
            "decomposition_stl", "ratios_conditionnels_regime", "choc_vol_parametrique",
        },
    },
    "modeles-validation": {
        "titre": "Modeles predictifs et validation",
        "description": (
            "Relations statistiques, previsions, tests hors echantillon et robustesse des modeles."
        ),
        "modeles": {
            "causalite_granger", "dependance_queue", "decomposition_variance", "test_chow",
            "arima", "walkforward_direction", "anomalie_multivariee", "test_overfitting",
            "prevision_vol_regression", "kmeans_regimes", "ensemble_signaux",
            "screening_features", "couts_transaction", "regression_multifeatures",
            "stacking", "decision_stump", "importance_permutation",
        },
    },
}

SORTIES_SPECIALES = {
    "walkforward_direction": "walkforward_direction_sp500",
    "test_overfitting": "test_overfitting_momentum",
}


def nom_court(nom_module: str) -> str:
    return nom_module.removeprefix("modele_")


def theme_du_modele(nom: str) -> str:
    trouves = [slug for slug, theme in THEMES.items() if nom in theme["modeles"]]
    if len(trouves) != 1:
        raise ValueError(f"{nom}: attendu dans un theme exactement, trouve {trouves}")
    return trouves[0]


def verifier_couverture() -> None:
    attendus = {nom_court(nom) for _, nom in MODELES}
    declares = [nom for theme in THEMES.values() for nom in theme["modeles"]]
    doublons = sorted(nom for nom, n in Counter(declares).items() if n > 1)
    manquants = sorted(attendus - set(declares))
    inconnus = sorted(set(declares) - attendus)
    if doublons or manquants or inconnus:
        raise ValueError(
            f"classification invalide: doublons={doublons}, manquants={manquants}, "
            f"inconnus={inconnus}"
        )


def _lire_lecture() -> dict[str, dict]:
    """Relit le rapport technique ou la derniere publication deja thematisee."""
    chemin = RAPPORTS / "lecture-du-jour.md"
    if not chemin.exists():
        raise FileNotFoundError("lecture-du-jour.md absent: lancer run_all_modeles.py d'abord")

    lectures = {}
    lanes = {nom_court(module): lane for lane, module in MODELES}
    lane = "inconnu"
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("## "):
            lane = ligne[3:].strip()
            continue
        match = re.match(r"^- \*\*(.+?)\*\* (?:--|—) (.*)$", ligne)
        if not match:
            continue
        libelle, lecture = match.groups()
        nom = libelle.strip().lower().replace(" ", "_")
        if nom not in lanes:
            continue
        lecture = re.sub(r"\s+_\(observation : .*?\)_$", "", lecture)
        lectures[nom] = {
            "lane": lanes.get(nom, lane),
            "lecture": lecture,
            "ok": "**[ECHEC]**" not in lecture,
            "synthese": "_(sans synthese)_" not in lecture,
        }
    return lectures


def _sortie(nom: str) -> Path | None:
    stem = SORTIES_SPECIALES.get(nom, nom)
    candidat = ETAT / f"{stem}.csv"
    return candidat if candidat.exists() else None


def _derniere_observation(chemin: Path | None) -> str | None:
    """Trouve la date la plus recente non future dans une sortie, sans inventer son schema."""
    if chemin is None:
        return None
    aujourd_hui = date.today()
    dates = []
    with chemin.open(encoding="utf-8", newline="") as flux:
        for ligne in csv.DictReader(flux):
            for valeur in ligne.values():
                if not valeur:
                    continue
                match = re.search(r"(?<!\d)(\d{4})[-_]?([01]\d)[-_]?([0-3]\d)(?!\d)",
                                  valeur.strip())
                if not match:
                    continue
                try:
                    valeur_date = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                except ValueError:
                    continue
                if valeur_date <= aujourd_hui:
                    dates.append(valeur_date)
    return max(dates).isoformat() if dates else None


def _resume_fraicheur() -> tuple[Counter, list[dict]]:
    chemin = ETAT / "fraicheur.csv"
    if not chemin.exists():
        return Counter(), []
    with chemin.open(encoding="utf-8", newline="") as flux:
        lignes = list(csv.DictReader(flux))
    return Counter(ligne.get("verdict", "INCONNU") for ligne in lignes), lignes


def _alertes_controles() -> list[str]:
    alertes = []
    coherence = ETAT / "coherence_fed.csv"
    if coherence.exists():
        with coherence.open(encoding="utf-8", newline="") as flux:
            lignes = list(csv.DictReader(flux))
        if lignes and lignes[-1].get("statut", "").lower() != "ok":
            derniere = lignes[-1]
            alertes.append(
                "Coherence Fed/BIS : **warning** — " + derniere.get("message", "ecart detecte")
            )
    ruptures = ETAT / "ruptures_perimetre.csv"
    if ruptures.exists():
        with ruptures.open(encoding="utf-8", newline="") as flux:
            lignes = list(csv.DictReader(flux))
        n_ruptures = sum(ligne.get("nature") == "perimetre" for ligne in lignes)
        if n_ruptures:
            alertes.append(
                f"Ruptures de perimetre : **{n_ruptures}** changement(s) structurel(s) "
                "documente(s) ; les historiques situes de part et d'autre ne sont pas directement "
                "comparables."
            )
    return alertes


def _liens_modele(nom: str, depuis_theme: bool = False) -> str:
    prefixe = ".." if depuis_theme else "."
    stem = SORTIES_SPECIALES.get(nom, nom)
    liens = []
    if (DONNEES_PUBLIEES / f"{stem}.csv").exists():
        liens.append(f"[donnees]({prefixe}/donnees/{stem}.csv)")
    dossier = GRAPHIQUES_PUBLIES / stem
    graphiques = sorted(dossier.glob("*.png")) if dossier.exists() else []
    if graphiques:
        choisi = next((p for p in graphiques if p.name == "apercu.png"), graphiques[0])
        liens.append(f"[graphique]({prefixe}/graphiques/{stem}/{choisi.name})")
    return " · ".join(liens)


def _bloc_modele(entree: dict, depuis_theme: bool = False) -> str:
    statut = "OK" if entree["ok"] else "ECHEC"
    date_obs = entree["derniere_observation"] or "non exposee par la sortie"
    liens = _liens_modele(entree["nom"], depuis_theme)
    meta = (
        f"Statut **{statut}** · observation {date_obs} · "
        f"moteur `{entree['lane']}`"
    )
    if liens:
        meta += " · " + liens
    return f"### {entree['titre']}\n\n{entree['lecture']}\n\n_{meta}_\n"


def _ecrire_qualite(genere_le: str, resultats: list[dict]) -> None:
    compte, lignes_fraicheur = _resume_fraicheur()
    alertes = [ligne for ligne in lignes_fraicheur if ligne.get("verdict") != "OK"]
    echecs = [r for r in resultats if not r["ok"]]
    alertes_controles = _alertes_controles()
    lignes = [
        "# Qualite et fraicheur", "",
        f"Derniere publication : **{genere_le}**.", "",
        "La date de publication indique quand les modeles ont ete recalcules. La date de "
        "derniere observation indique quand la source a publie sa derniere valeur ; une serie "
        "mensuelle ou trimestrielle peut donc etre saine sans porter la date du jour.", "",
        "## Calculs", "",
        f"- {len(resultats) - len(echecs)}/{len(resultats)} modeles reussis",
        f"- {len(echecs)} echec(s)", "",
        "## Sources", "",
        f"- {sum(compte.values())} series controlees",
        f"- {compte.get('OK', 0)} normales",
        f"- {compte.get('SUSPECTE', 0)} suspectes",
        f"- {compte.get('GELEE', 0)} gelees", "",
    ]
    if alertes:
        lignes += ["### Sources a examiner", "", "| Serie | Derniere observation | Statut |",
                   "|---|---:|---|"]
        for alerte in alertes:
            lignes.append(
                f"| `{alerte.get('serie', '')}` | {alerte.get('derniere_observation', '')} | "
                f"**{alerte.get('verdict', '')}** |"
            )
        lignes.append("")
    else:
        lignes += ["Aucune source suspecte ou gelee.", ""]
    lignes += ["## Controles de coherence et de perimetre", ""]
    if alertes_controles:
        lignes += [f"- {alerte}" for alerte in alertes_controles]
    else:
        lignes.append("- Aucun avertissement de coherence ou de perimetre.")
    lignes += ["", "Les fichiers de controle complets sont disponibles dans "
               "[les donnees publiees](donnees/).", ""]
    (RAPPORTS / "qualite.md").write_text("\n".join(lignes), encoding="utf-8")


def publier() -> int:
    verifier_couverture()
    lectures = _lire_lecture()

    maintenant = datetime.now(timezone.utc)
    genere_le = maintenant.strftime("%Y-%m-%d %H:%M UTC")
    resultats = []
    for lane, module in MODELES:
        nom = nom_court(module)
        lecture = lectures.get(nom, {
            "lane": lane,
            "lecture": "Lecture absente du dernier calcul.",
            "ok": False,
            "synthese": False,
        })
        sortie = _sortie(nom)
        resultats.append({
            "nom": nom,
            "titre": nom.replace("_", " ").capitalize(),
            "theme": theme_du_modele(nom),
            "lane": lecture["lane"],
            "lecture": lecture["lecture"],
            "ok": lecture["ok"],
            "synthese": lecture["synthese"],
            "sortie": sortie.name if sortie else None,
            "derniere_observation": _derniere_observation(sortie),
        })

    THEMES_DIR.mkdir(parents=True, exist_ok=True)
    for slug, theme in THEMES.items():
        membres = [r for r in resultats if r["theme"] == slug]
        lignes = [f"# {theme['titre']}", "", theme["description"], "",
                  f"Mis a jour : **{genere_le}** · {len(membres)} lectures.", "",
                  "[Retour au tableau de bord](../README.md)", ""]
        for entree in membres:
            lignes += [_bloc_modele(entree, depuis_theme=True), ""]
        (THEMES_DIR / f"{slug}.md").write_text("\n".join(lignes), encoding="utf-8")

    compte_fraicheur, _ = _resume_fraicheur()
    echecs = sum(not r["ok"] for r in resultats)
    sans_synthese = sum(r["ok"] and not r["synthese"] for r in resultats)
    alertes_controles = _alertes_controles()
    coherence_en_warning = any(alerte.startswith("Coherence") for alerte in alertes_controles)
    etat_global = "ECHEC" if echecs else (
        "ATTENTION" if (compte_fraicheur.get("SUSPECTE", 0)
                        or compte_fraicheur.get("GELEE", 0) or coherence_en_warning)
        else "OK"
    )

    entete = [
        f"# Rapport global — {genere_le}", "",
        f"**Etat global : {etat_global}** · {len(resultats) - echecs}/{len(resultats)} modeles "
        f"reussis · {compte_fraicheur.get('SUSPECTE', 0)} source(s) suspecte(s) · "
        f"{compte_fraicheur.get('GELEE', 0)} source(s) gelee(s).", "",
        "Cette page regroupe toutes les conclusions. Les calculs sont actualises chaque heure ; "
        "les observations conservent la cadence de publication de leur source officielle.", "",
        f"{sans_synthese} lecture(s) restent signalees sans synthese lorsque le modele enumere "
        "des resultats sans produire de conclusion globale.", "",
        "[Qualite et fraicheur](qualite.md) · [Classeur complet](etat-recherche.xlsx) · "
        "[Toutes les donnees](donnees/) · [Tous les graphiques](graphiques/)", "",
    ]
    lignes_globales = list(entete)
    for slug, theme in THEMES.items():
        membres = [r for r in resultats if r["theme"] == slug]
        lignes_globales += [f"## [{theme['titre']}](themes/{slug}.md)", "", theme["description"], ""]
        for entree in membres:
            statut = "" if entree["ok"] else "**[ECHEC]** "
            obs = entree["derniere_observation"] or "date non exposee"
            lignes_globales.append(
                f"- **{entree['titre']}** — {statut}{entree['lecture']} "
                f"_(observation : {obs})_"
            )
        lignes_globales.append("")
    (RAPPORTS / "lecture-du-jour.md").write_text("\n".join(lignes_globales), encoding="utf-8")

    accueil = [
        "# Centre de recherche", "",
        "**C'est le point d'entree unique du depot.** Les scripts et fichiers techniques restent "
        "hors de cette vue ; toutes les conclusions, donnees publiees et visualisations sont "
        "rassemblees ici.", "",
        f"Derniere publication : **{genere_le}** · Etat **{etat_global}** · "
        f"{len(resultats) - echecs}/{len(resultats)} modeles reussis.", "",
        "## Commencer ici", "",
        "1. [Lire le rapport global](lecture-du-jour.md)",
        "2. [Verifier la qualite et la fraicheur](qualite.md)",
        "3. [Ouvrir le classeur complet](etat-recherche.xlsx)", "",
        "## Rapports thematiques", "",
    ]
    for slug, theme in THEMES.items():
        n = sum(r["theme"] == slug for r in resultats)
        accueil.append(f"- [{theme['titre']}](themes/{slug}.md) — {n} lectures")
    accueil += ["", "## Toutes les sorties", "",
                "- [Donnees](donnees/) — source unique de tous les CSV produits",
                "- [Graphiques utiles](graphiques/) — uniquement quand le visuel apporte une lecture",
                "- [Inventaire automatique](inventaire.md) — couverture du dispositif", ""]
    (RAPPORTS / "README.md").write_text("\n".join(accueil), encoding="utf-8")
    _ecrire_qualite(genere_le, resultats)

    manifeste = {
        "generated_at": maintenant.isoformat(),
        "status": etat_global.lower(),
        "models": resultats,
        "freshness": dict(compte_fraicheur),
    }
    (RAPPORTS / "latest.json").write_text(
        json.dumps(manifeste, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"OK -- centre de recherche publie : {len(resultats)} modeles, "
        f"{len(THEMES)} themes, etat {etat_global} -> rapports/README.md"
    )
    return 0


def main() -> int:
    try:
        return publier()
    except (OSError, ValueError, csv.Error) as erreur:
        print(f"echec -- publication des rapports : {erreur}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
