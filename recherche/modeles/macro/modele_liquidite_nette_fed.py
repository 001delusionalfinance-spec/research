"""Modele -- liquidite nette du systeme americain.

actif total de la Fed - compte general du Tresor - reverse repo total

L'actif total de la Fed seul ne dit pas combien de liquidite circule reellement dans le systeme
bancaire. Deux poches en retirent sans qu'aucune decision de politique monetaire ne soit prise :

- **Le compte du Tresor a la Fed.** Quand le Tresor encaisse plus qu'il ne depense, son compte
  se remplit et autant de reserves quittent les banques. Quand il se vide, elles y reviennent.
  Un mouvement de plusieurs centaines de milliards passe ainsi sans reunion ni communique.
- **Le reverse repo.** Les fonds monetaires y placent leurs liquidites aupres de la Fed ; ce qui
  y est gare ne circule plus.

Les trois composantes viennent du **meme releve hebdomadaire H.4.1** (WALCL, WTREGEN, WLRRAL).
C'est deliberé : le solde de tresorerie est aussi ingere en quotidien cote Tresor, mais melanger
deux sources aux dates de publication differentes produirait une difference fausse aux
jointures. Meme releve, memes dates, difference propre.

Limite : mesure americaine uniquement. Il n'existe pas d'equivalent construit ici pour la zone
euro ou le Japon.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import BRUT, ETAT, SerieVide, accumuler_csv, read_series  # noqa: E402

NOM_MODELE = "liquidite_nette_fed"
FRED = BRUT / "fred"
SEUIL_MOUVEMENT_PCT = 1.0


def aligner(series: dict) -> list:
    """Dates communes aux trois series -- une difference n'a de sens qu'a date identique."""
    ensembles = [set(d for d, _ in s) for s in series.values()]
    communes = sorted(set.intersection(*ensembles))
    if not communes:
        raise SerieVide("aucune date commune entre actif total, compte du Tresor et reverse repo")
    index = {nom: dict(s) for nom, s in series.items()}
    return [(d, {nom: index[nom][d] for nom in series}) for d in communes]


def valeur_il_y_a(points: list, jours: int) -> float:
    cible = date.fromisoformat(points[-1][0]) - timedelta(days=jours)
    anterieurs = [v for d, v in points if date.fromisoformat(d) <= cible]
    if not anterieurs:
        raise SerieVide(f"aucun point {jours} jours avant la derniere observation")
    return anterieurs[-1]


def main() -> int:
    try:
        brutes = {
            "actif": read_series(FRED / "WALCL.csv"),
            "tresor": read_series(FRED / "WTREGEN.csv"),
            "reverse_repo": read_series(FRED / "WLRRAL.csv"),
        }
        alignees = aligner(brutes)
    except SerieVide as e:
        print(f"echec -- {e}")
        return 1

    liquidite = [(d, v["actif"] - v["tresor"] - v["reverse_repo"]) for d, v in alignees]
    derniere_date, niveau = liquidite[-1]
    composantes = dict(alignees[-1][1])

    try:
        var_3m = (niveau / valeur_il_y_a(liquidite, 91) - 1) * 100
        var_12m = (niveau / valeur_il_y_a(liquidite, 365) - 1) * 100
    except (SerieVide, ZeroDivisionError) as e:
        print(f"echec -- {e}")
        return 1

    accumuler_csv(
        ETAT / f"{NOM_MODELE}.csv",
        ["date", "liquidite_nette_musd", "actif_total_musd", "compte_tresor_musd",
         "reverse_repo_musd", "variation_3m_pct", "variation_12m_pct"],
        [[derniere_date, round(niveau, 1), round(composantes["actif"], 1),
          round(composantes["tresor"], 1), round(composantes["reverse_repo"], 1),
          round(var_3m, 2), round(var_12m, 2)]],
    )

    if var_3m < -SEUIL_MOUVEMENT_PCT:
        lecture = "liquidite en retrait sur 3 mois -- conditions de financement qui se durcissent"
    elif var_3m > SEUIL_MOUVEMENT_PCT:
        lecture = "liquidite en apport sur 3 mois -- conditions qui se detendent"
    else:
        lecture = "liquidite stable sur 3 mois"

    print(f"OK -- liquidite nette {niveau / 1e6:.2f} T$ au {derniere_date} "
          f"({var_3m:+.1f}% sur 3 mois, {var_12m:+.1f}% sur 12 mois) -- {lecture}. "
          f"Detail : actif {composantes['actif'] / 1e6:.2f} T$, "
          f"compte du Tresor {composantes['tresor'] / 1e6:.2f} T$, "
          f"reverse repo {composantes['reverse_repo'] / 1e6:.2f} T$")
    return 0


if __name__ == "__main__":
    sys.exit(main())
