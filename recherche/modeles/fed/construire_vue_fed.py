"""Construit la vue produit Fed a partir des sorties de recherche existantes.

Les modeles restent classes par methode dans ``recherche/modeles``. Cette couche ne recalcule
rien : elle transforme leurs resultats en un contrat stable, organise selon les questions que
se pose un lecteur de la Fed (position, reaction, marche, liquidite, communication).
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
MODELES = REPO_ROOT / "recherche" / "modeles"
ETAT = REPO_ROOT / "recherche" / "etat"
BRUT = REPO_ROOT / "donnees" / "brut"
SORTIE = REPO_ROOT / "rapports" / "fed"

sys.path.insert(0, str(MODELES))
from _lib import accumuler_csv  # noqa: E402

SCHEMA_VERSION = "1.0"


def lire_csv(nom: str, dossier: Path = ETAT) -> list[dict]:
    chemin = dossier / nom
    if not chemin.exists():
        return []
    with chemin.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def normaliser_date(texte: str) -> str:
    texte = str(texte or "").strip()
    if len(texte) == 8 and texte.isdigit():
        return f"{texte[:4]}-{texte[4:6]}-{texte[6:]}"
    return texte


def date_de(ligne: dict) -> str:
    for cle in ("date", "date_controle", "date_fomc", "date_reunion", "periode"):
        if ligne.get(cle):
            return normaliser_date(ligne[cle])
    return ""


def derniere(nom: str) -> dict:
    lignes = lire_csv(nom)
    return max(lignes, key=lambda ligne: date_de(ligne), default={})


def nombre(valeur):
    if valeur is None or valeur == "":
        return None
    try:
        resultat = float(valeur)
        return int(resultat) if resultat.is_integer() else resultat
    except (TypeError, ValueError):
        return valeur


def fraicheur(as_of: str, seuil_jours: int) -> tuple[int | None, str]:
    try:
        jours = max(0, (date.today() - date.fromisoformat(as_of)).days)
    except (TypeError, ValueError):
        return None, "missing"
    return jours, "ok" if jours <= seuil_jours else "stale"


def metrique(*, identifiant: str, label: str, value, unit: str, as_of: str, source: str,
             confidence: str, methodology: str, stale_after_days: int,
             status: str | None = None) -> dict:
    age, statut_fraicheur = fraicheur(as_of, stale_after_days)
    statut = status or statut_fraicheur
    if value is None:
        statut = "missing"
    return {
        "id": identifiant,
        "label": label,
        "value": nombre(value),
        "unit": unit,
        "as_of": as_of,
        "source": source,
        "freshness_days": age,
        "status": statut,
        "confidence": confidence,
        "methodology": methodology,
    }


def fourchette_fomc() -> tuple[dict, float | None]:
    lignes = lire_csv("votes.csv", BRUT / "fomc")
    lignes = [ligne for ligne in lignes if ligne.get("taux_cible")]
    if not lignes:
        return {}, None
    ligne = max(lignes, key=date_de)
    try:
        from controle_coherence_fed import milieu_fourchette
        return ligne, milieu_fourchette(ligne["taux_cible"])
    except (ValueError, IndexError):
        return ligne, None


def construire_sections() -> list[dict]:
    vote, milieu = fourchette_fomc()
    reel = derniere("taux_reel_us.csv")
    taylor = derniere("regle_taylor.csv")
    sahm = derniere("sahm_rule.csv")
    conditions = derniere("conditions_financieres.csv")
    surprise = derniere("surprise_inflation.csv")
    courbe = derniere("courbe_taux_us.csv")
    liquidite = derniere("liquidite_nette_fed.csv")
    ton = derniere("ton_fomc.csv")
    desaccord = derniere("intensite_desaccord.csv")
    coherence = derniere("coherence_fed.csv")

    chemins = lire_csv("chemin_taux_fed.csv")
    date_chemin = max((date_de(ligne) for ligne in chemins), default="")
    chemins = [ligne for ligne in chemins if date_de(ligne) == date_chemin]

    sections = [
        {
            "id": "position_actuelle",
            "label": "Position actuelle",
            "metrics": [
                metrique(
                    identifiant="fed_target_midpoint", label="Milieu de la cible FOMC",
                    value=milieu, unit="%", as_of=date_de(vote), source="Federal Reserve/FOMC",
                    confidence="haute", methodology="Milieu de la fourchette officielle",
                    stale_after_days=65,
                ),
                metrique(
                    identifiant="fed_effective_rate", label="Taux Fed effectif",
                    value=reel.get("taux_nominal_pct"), unit="%", as_of=date_de(reel),
                    source="FRED DFF", confidence="haute",
                    methodology="Derniere observation du taux effectif", stale_after_days=5,
                ),
                metrique(
                    identifiant="fed_real_rate", label="Taux réel ex post",
                    value=reel.get("taux_reel_pct"), unit="%", as_of=date_de(reel),
                    source="FRED DFF et CPIAUCSL", confidence="moyenne",
                    methodology="Taux effectif moins inflation CPI realisee en glissement annuel",
                    stale_after_days=40,
                ),
            ],
        },
        {
            "id": "fonction_reaction",
            "label": "Fonction de réaction",
            "metrics": [
                metrique(
                    identifiant="taylor_gap", label="Écart Fed - Taylor",
                    value=taylor.get("ecart_pt"), unit="point", as_of=date_de(taylor),
                    source="Modèle Taylor interne", confidence="faible",
                    methodology="Taylor à deux termes sans output gap", stale_after_days=40,
                ),
                metrique(
                    identifiant="sahm_gap", label="Écart règle de Sahm",
                    value=sahm.get("ecart_pt"), unit="point", as_of=date_de(sahm),
                    source="FRED UNRATE", confidence="haute",
                    methodology="MM3 chômage moins son plus bas sur 12 mois", stale_after_days=40,
                ),
                metrique(
                    identifiant="financial_conditions", label="Conditions financières",
                    value=conditions.get("indice_composite"), unit="score z",
                    as_of=date_de(conditions), source="Composite interne", confidence="moyenne",
                    methodology="Taux directeur, pente de courbe et VIX standardisés",
                    stale_after_days=5,
                ),
                metrique(
                    identifiant="inflation_surprise", label="Surprise inflation",
                    value=surprise.get("surprise_pt"), unit="point", as_of=date_de(surprise),
                    source="FRED CPIAUCSL", confidence="faible",
                    methodology="Publication CPI mensuelle moins prévision naïve",
                    stale_after_days=45,
                ),
            ],
        },
        {
            "id": "anticipations_marche",
            "label": "Anticipations de marché",
            "metrics": [
                metrique(
                    identifiant=f"rate_path_{ligne.get('horizon', '').replace(' ', '_')}",
                    label=f"Mouvement implicite {ligne.get('horizon', '')}",
                    value=ligne.get("mouvement_implicite_pb"), unit="pb",
                    as_of=date_de(ligne), source=ligne.get("methode", "forward_treasury_proxy"),
                    confidence=ligne.get("confiance", "faible"),
                    methodology=ligne.get("limite", "Mouvement net; pas une probabilité"),
                    stale_after_days=4,
                ) for ligne in chemins
            ] + [
                metrique(
                    identifiant="yield_curve_10y2y", label="Pente Treasury 10a-2a",
                    value=courbe.get("spread_pt"), unit="point", as_of=date_de(courbe),
                    source="FRED DGS10/DGS2", confidence="haute",
                    methodology="Rendement 10 ans moins rendement 2 ans", stale_after_days=4,
                ),
            ],
        },
        {
            "id": "liquidite_bilan",
            "label": "Liquidité et bilan",
            "metrics": [
                metrique(
                    identifiant="fed_net_liquidity", label="Liquidité nette Fed",
                    value=liquidite.get("liquidite_nette_musd"), unit="M$",
                    as_of=date_de(liquidite), source="Fed H.4.1 via FRED", confidence="moyenne",
                    methodology="WALCL - compte du Trésor - reverse repo", stale_after_days=12,
                ),
                metrique(
                    identifiant="fed_net_liquidity_3m", label="Variation liquidité sur 3 mois",
                    value=liquidite.get("variation_3m_pct"), unit="%",
                    as_of=date_de(liquidite), source="Fed H.4.1 via FRED", confidence="moyenne",
                    methodology="Variation du proxy de liquidité nette", stale_after_days=12,
                ),
            ],
        },
        {
            "id": "communication",
            "label": "Communication",
            "metrics": [
                metrique(
                    identifiant="fomc_tone_change", label="Variation du ton FOMC",
                    value=ton.get("diff_score_pour_mille"), unit="‰", as_of=date_de(ton),
                    source="Communiqués FOMC", confidence="faible",
                    methodology="Différence d'un lexique interne entre deux communiqués",
                    stale_after_days=65,
                ),
                metrique(
                    identifiant="fomc_dissenters", label="Dissidents au vote",
                    value=ton.get("nb_dissidents"), unit="membres", as_of=date_de(ton),
                    source="Communiqué FOMC", confidence="haute",
                    methodology="Comptage des votes contre la décision", stale_after_days=65,
                ),
                metrique(
                    identifiant="minutes_disagreement", label="Mentions de désaccord",
                    value=desaccord.get("total_mentions"), unit="mentions",
                    as_of=date_de(desaccord), source="Minutes FOMC", confidence="faible",
                    methodology=("Comptage d'expressions de désaccord dans les minutes : "
                                 + desaccord.get("n_mentions_desaccord_texte", "")),
                    stale_after_days=90,
                ),
            ],
        },
    ]

    if coherence:
        sections[0]["metrics"].append(metrique(
            identifiant="fed_source_coherence", label="Cohérence FOMC / BIS",
            value=coherence.get("ecart_pt"), unit="point", as_of=date_de(coherence),
            source="FOMC et BIS WS_CBPOL", confidence="haute",
            methodology=coherence.get("message", "Contrôle de cohérence inter-sources"),
            stale_after_days=5, status=coherence.get("statut", "warning"),
        ))
    return sections


def valeur_affichee(metrique_: dict) -> str:
    valeur = metrique_["value"]
    if valeur is None:
        return "indisponible"
    if isinstance(valeur, float):
        valeur = f"{valeur:.3f}".rstrip("0").rstrip(".")
    return f"{valeur} {metrique_['unit']}".strip()


def ecrire_markdown(snapshot: dict) -> None:
    lignes = ["# Fed Research", "", f"**État global : {snapshot['status'].upper()}** · "
              f"données au {snapshot['as_of']}", ""]
    for avertissement in snapshot["warnings"]:
        lignes.append(f"> ⚠️ {avertissement}")
    if snapshot["warnings"]:
        lignes.append("")
    for section in snapshot["sections"]:
        lignes += [f"## {section['label']}", "",
                   "| Mesure | Valeur | Date | Statut | Confiance | Source |",
                   "|---|---:|---|---|---|---|"]
        for item in section["metrics"]:
            lignes.append(
                f"| {item['label']} | {valeur_affichee(item)} | {item['as_of'] or '—'} | "
                f"{item['status']} | {item['confidence']} | {item['source']} |")
        lignes.append("")
    lignes += ["## Convention", "",
               "Le chemin de taux est un **proxy de mouvement net**, pas une probabilité par "
               "réunion. `warning` signale une source retardée ou un proxy fragile ; `stale` "
               "signale une observation plus ancienne que sa cadence attendue.", ""]
    (SORTIE / "latest.md").write_text("\n".join(lignes), encoding="utf-8")


def main() -> int:
    sections = construire_sections()
    metriques = [item for section in sections for item in section["metrics"]]
    # Une date de controle n'est pas une date d'observation. L'ancien dashboard pouvait ainsi
    # paraitre "aujourd'hui" alors que son dernier prix remontait a plusieurs jours.
    dates = [item["as_of"] for item in metriques
             if item["as_of"] and item["id"] != "fed_source_coherence"]
    statuts = {item["status"] for item in metriques}
    statut = "error" if "missing" in statuts else (
        "warning" if statuts.intersection({"warning", "stale"}) else "ok")
    avertissements = [
        "Le chemin de taux dérivé des Treasuries ne constitue pas une distribution de "
        "probabilités par réunion FOMC."
    ]
    coherence = next((m for m in metriques if m["id"] == "fed_source_coherence"), None)
    if coherence and coherence["status"] == "warning":
        avertissements.append(coherence["methodology"])
    manquantes = [m["label"] for m in metriques if m["status"] == "missing"]
    if manquantes:
        avertissements.append("Mesures indisponibles : " + ", ".join(manquantes))

    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "product": "fed_research",
        "checked_on": date.today().isoformat(),
        "as_of": max(dates, default=""),
        "status": statut,
        "warnings": avertissements,
        "sections": sections,
    }
    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / "latest.json").write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (SORTIE / "health.json").write_text(
        json.dumps({
            "schema_version": SCHEMA_VERSION,
            "checked_on": date.today().isoformat(),
            "as_of": snapshot["as_of"],
            "status": statut,
            "counts": {etat: sum(m["status"] == etat for m in metriques)
                       for etat in ("ok", "warning", "stale", "missing")},
            "warnings": avertissements,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ecrire_markdown(snapshot)

    historique = [[m["as_of"], m["id"], m["value"], m["unit"], m["status"],
                   m["confidence"], m["source"]] for m in metriques if m["as_of"]]
    accumuler_csv(
        SORTIE / "history.csv",
        ["as_of", "metric_id", "value", "unit", "status", "confidence", "source"],
        historique,
        key_columns=["as_of", "metric_id"],
    )
    print(f"OK -- vue Fed {statut}, {len(metriques)} mesures, donnees au {snapshot['as_of']}")
    return 0 if statut != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
