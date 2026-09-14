"""Modele -- positionnement speculatif sur les devises du G10 et le peso mexicain.

Lit les contrats de change du rapport COT et croise le positionnement net avec le differentiel
de taux directeur correspondant.

**Le croisement est le point du modele.** Un positionnement long sur une devise n'a pas le meme
sens selon qu'il est adosse a un differentiel de taux favorable ou non. Long une devise a haut
rendement, c'est du carry -- une position qui se paie tant que rien ne bouge, et se deboucle
brutalement quand la volatilite monte. Long une devise a bas rendement, c'est un pari
directionnel qui coute a porter, donc une conviction plus forte. Le meme chiffre de
positionnement raconte deux histoires opposees.

Le positionnement net est ramene a son rang en percentile sur tout l'historique : les contrats
n'ont ni la meme taille ni la meme liquidite, leurs niveaux bruts ne se comparent pas.

Rappel de convention : les contrats de la CFTC cotent la devise etrangere CONTRE le dollar. Un
net positif est donc toujours un pari haussier sur la devise etrangere, jamais sur le dollar.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _lib import (BRUT, ETAT, SerieVide, ecrire_csv,  # noqa: E402
                  percentile_rang, read_series)

NOM_MODELE = "positionnement_devises"
COT = BRUT / "cftc"
TAUX = BRUT / "bis" / "taux_directeurs"

# (libelle, contrat COT, code du bloc pour le taux directeur)
DEVISES = [
    ("Euro", "EUR_FX", "XM"),
    ("Yen", "JPY_FX", "JP"),
    ("Livre sterling", "GBP_FX", "GB"),
    ("Dollar canadien", "CAD_FX", "CA"),
    ("Dollar australien", "AUD_FX", "AU"),
    ("Franc suisse", "CHF_FX", "CH"),
    ("Dollar neo-zelandais", "NZD_FX", "NZ"),
    ("Peso mexicain", "MXN_FX", None),   # pas de taux directeur mexicain ingere
]
SEUIL_EXTREME = 85.0
SEUIL_BAS = 15.0


def taux_us() -> float:
    return read_series(TAUX / "US.csv", "taux")[-1][1]


def main() -> int:
    try:
        reference = taux_us()
    except (SerieVide, ValueError) as e:
        print(f"echec -- taux directeur americain indisponible ({e})")
        return 1

    lignes, echecs = [], []
    for libelle, contrat, code in DEVISES:
        try:
            serie = read_series(COT / f"{contrat}.csv", "noncomm_net")
            historique = [v for _, v in serie]
            if len(historique) < 52:
                raise SerieVide(f"seulement {len(historique)} semaines")
            net = serie[-1][1]
            rang = percentile_rang(net, historique)
            sens = "long" if net > 0 else ("short" if net < 0 else "neutre")

            differentiel = ""
            nature = "differentiel inconnu"
            if code:
                try:
                    differentiel = read_series(TAUX / f"{code}.csv", "taux")[-1][1] - reference
                    if sens == "long" and differentiel > 0.25:
                        nature = "carry (long une devise mieux remuneree)"
                    elif sens == "long" and differentiel < -0.25:
                        nature = "pari directionnel couteux (long une devise moins remuneree)"
                    elif sens == "short" and differentiel > 0.25:
                        nature = "short contre le carry (position qui coute a porter)"
                    elif sens == "short":
                        nature = "short adosse au differentiel"
                    else:
                        nature = "differentiel neutre"
                    differentiel = round(differentiel, 2)
                except (SerieVide, ValueError):
                    differentiel = ""

            if rang >= SEUIL_EXTREME:
                extremite = "extreme haut"
            elif rang <= SEUIL_BAS:
                extremite = "extreme bas"
            else:
                extremite = "median"

            lignes.append((libelle, contrat, serie[-1][0], int(net), round(rang, 1),
                           differentiel, sens, nature, extremite))
        except (SerieVide, ValueError) as e:
            echecs.append((libelle, str(e)))

    if not lignes:
        print(f"echec -- aucune devise exploitable ({len(echecs)} en erreur)")
        return 1

    lignes.sort(key=lambda l: -l[4])
    ecrire_csv(ETAT / f"{NOM_MODELE}.csv",
               ["devise", "contrat", "date", "position_nette_speculative",
                "percentile_historique", "differentiel_taux_vs_us_pt", "sens",
                "nature_de_la_position", "extremite"], lignes)

    carry = [l[0] for l in lignes if l[7].startswith("carry")]
    extremes = [f"{l[0]} ({l[8]}, {l[4]:.0f}e pct)" for l in lignes if l[8] != "median"]

    lecture = (f"{len(carry)} position(s) de type carry : {', '.join(carry)}" if carry
               else "aucune position de carry identifiee")
    if extremes:
        lecture += (f". A un extreme historique : {', '.join(extremes)} -- un positionnement "
                    f"extreme est vulnerable a un deboucle rapide si la volatilite monte")

    print(f"OK -- {len(lignes)} devises (net positif = pari haussier sur la devise etrangere, "
          f"jamais sur le dollar) -- {lecture}")
    if echecs:
        print(f"   {len(echecs)} devise(s) non exploitable(s) : {[n for n, _ in echecs]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
