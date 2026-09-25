"""Recalcule uniquement les briques utiles a la vue Fed puis publie son contrat de sortie."""

import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent

ETAPES = [
    "macro/modele_sahm_rule.py",
    "macro/modele_taux_reel_us.py",
    "macro/modele_regle_taylor.py",
    "macro/modele_courbe_taux_us.py",
    "macro/modele_chemin_taux_fed.py",
    "macro/modele_conditions_financieres.py",
    "macro/modele_liquidite_nette_fed.py",
    "macro/modele_surprise_inflation.py",
    "nlp/modele_ton_fomc.py",
    "nlp/modele_frequence_mots_cles_fomc.py",
    "nlp/modele_complexite_texte_fomc.py",
    "nlp/modele_ton_minutes_fomc.py",
    "nlp/modele_ecart_communique_minutes.py",
    "nlp/modele_intensite_desaccord.py",
    "controle_coherence_fed.py",
]


def executer(relatif: str) -> bool:
    chemin = ICI / relatif
    print(f"\n--- {relatif} ---", flush=True)
    resultat = subprocess.run([sys.executable, str(chemin)], cwd=ICI, check=False)
    return resultat.returncode == 0


def main() -> int:
    echecs = [etape for etape in ETAPES if not executer(etape)]
    vue_ok = executer("fed/construire_vue_fed.py")
    if not vue_ok:
        echecs.append("fed/construire_vue_fed.py")
    print(f"\n=== Fed : {len(ETAPES) + 1 - len(echecs)}/{len(ETAPES) + 1} etapes OK ===")
    if echecs:
        print(f"En echec : {echecs}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
