# Banques centrales et politique monetaire

Decisions, fonctions de reaction, bilan, communication et trajectoires de taux.

Mis a jour : **2026-09-25 07:53 UTC** · 19 lectures.

[Retour au tableau de bord](../README.md)

### Regime monetaire emploi

Chine : taux 1.54% (stable, niveau bas) -- chomage non_couvert  _(sans synthese)_

_Statut **OK** · observation 2026-09-18 · moteur `macro` · [donnees](../donnees/regime_monetaire_emploi.csv) · [graphique](../graphiques/regime_monetaire_emploi/apercu.png)_


### Regle taylor

Taylor (2 termes, sans output gap)=6.03%, Fed reel=3.88%, ecart=-2.15pt -- accommodant (Fed en-dessous de la regle)

_Statut **OK** · observation 2026-09-18 · moteur `macro` · [donnees](../donnees/regle_taylor.csv) · [graphique](../graphiques/regle_taylor/apercu.png)_


### Chemin taux fed

chemin de taux (pas des probabilites) : DFF=3.88%, prochaine reunion 2026-10-27 (11 a venir dans le calendrier) -- 0-1 mois: +9pb (hausse, confiance faible) | 1-3 mois: +34pb (hausse, confiance faible) | 3-6 mois: +46pb (hausse, confiance faible) | 6-12 mois: +76pb (hausse, confiance faible)

_Statut **OK** · observation 2026-09-22 · moteur `macro` · [donnees](../donnees/chemin_taux_fed.csv) · [graphique](../graphiques/chemin_taux_fed/apercu.png)_


### Divergence taux directeurs

12 banques centrales : ecart de taux max 4.35pt (Australie 4.35% contre Suisse 0.00%), mediane 2.88% -- cycles alignes dans le meme sens (resserrement) -- divergence limitee

_Statut **OK** · observation 2026-09-15 · moteur `macro` · [donnees](../donnees/divergence_taux_directeurs.csv) · [graphique](../graphiques/divergence_taux_directeurs/apercu.png)_


### Bilans banques centrales

9 bilans suivis sur 12 mois : de -14.9% (RBA -- titres locaux) a +8.4% (Fed -- titres du Tresor) -- regimes OPPOSES -- 5 bilan(s) en reduction pendant que 3 s'etendent, la liquidite mondiale ne va pas dans un sens unique

_Statut **OK** · observation 2026-09-16 · moteur `macro` · [donnees](../donnees/bilans_banques_centrales.csv) · [graphique](../graphiques/bilans_banques_centrales/apercu.png)_


### Liquidite nette fed

liquidite nette 5.55 T$ au 2026-09-16 (+0.5% sur 3 mois, -0.1% sur 12 mois) -- liquidite stable sur 3 mois. Detail : actif 6.75 T$, compte du Tresor 0.88 T$, reverse repo 0.32 T$

_Statut **OK** · observation 2026-09-16 · moteur `macro` · [donnees](../donnees/liquidite_nette_fed.csv) · [graphique](../graphiques/liquidite_nette_fed/apercu.png)_


### Ton banques centrales

variation du ton depuis la publication precedente, par institution (pour mille, meme lexique) : Fed +21.98, BCE +12.50, Banque d'Angleterre +8.79 -- detente du ton chez Fed, BCE, Banque d'Angleterre. Les niveaux ne sont PAS comparables entre institutions : un seul mot de ton les deplace de Fed 8.8, BCE 0.6, Banque d'Angleterre 0.1 pour mille respectivement, selon la longueur du document

_Statut **OK** · observation 2026-09-17 · moteur `nlp` · [donnees](../donnees/ton_banques_centrales.csv) · [graphique](../graphiques/ton_banques_centrales/apercu.png)_


### Ton fomc

20260729 -> 20260916 : ton +13.42‰ -> +35.40‰ (diff +21.98‰, ton qui s'ameliore), taux change (3-3/4 to 4), dissidents 3 -> 0

_Statut **OK** · observation 2026-09-16 · moteur `nlp` · [donnees](../donnees/ton_fomc.csv) · [graphique](../graphiques/ton_fomc/apercu.png)_


### Frequence mots cles fomc

communique 20260916, 114 mots -- mots-cles presents : {'uncertainty': 1, 'elevated': 2, 'solid': 1, 'strong': 1, 'resilient': 1} -- theme dominant : 'elevated' (2 mention(s))

_Statut **OK** · observation 2026-09-16 · moteur `nlp` · [donnees](../donnees/frequence_mots_cles_fomc.csv) · [graphique](../graphiques/frequence_mots_cles_fomc/apercu.png)_


### Complexite texte fomc

communique 20260916 : 113 mots, 9 phrases (12.6 mots/phrase en moyenne, phrases de longueur moderee), 36.3% de mots longs (>6 lettres, vocabulaire dense)

_Statut **OK** · observation 2026-09-16 · moteur `nlp` · [donnees](../donnees/complexite_texte_fomc.csv) · [graphique](../graphiques/complexite_texte_fomc/apercu.png)_


### Ton minutes fomc

20260617 -> 20260729 : ton +2.49pm -> +3.97pm (diff +1.49pm, ton qui s'ameliore), 4780 mots (67 positifs, 48 negatifs)

_Statut **OK** · observation 2026-07-29 · moteur `nlp` · [donnees](../donnees/ton_minutes_fomc.csv) · [graphique](../graphiques/ton_minutes_fomc/apercu.png)_


### Ecart communique minutes

reunion 20260729 : communique=+13.42pm, minutes=+3.97pm -- ecart=+9.45pm (communique plus positif)

_Statut **OK** · observation 2026-07-29 · moteur `nlp` · [donnees](../donnees/ecart_communique_minutes.csv) · [graphique](../graphiques/ecart_communique_minutes/apercu.png)_


### Complexite texte minutes

minutes 20260729 : 4780 mots, 231 phrases (20.7 mots/phrase, phrases longues), 35.6% de mots longs (>6 lettres, vocabulaire dense)

_Statut **OK** · observation 2026-07-29 · moteur `nlp` · [donnees](../donnees/complexite_texte_minutes.csv) · [graphique](../graphiques/complexite_texte_minutes/apercu.png)_


### Entites geographiques minutes

minutes 20260729 -- mentions : {'Middle East': 12, 'labor_market': 22, 'inflation': 51, 'tariffs': 7, 'housing': 3} -- focus dominant : 'inflation' (51 mention(s))

_Statut **OK** · observation 2026-07-29 · moteur `nlp` · [donnees](../donnees/entites_geographiques_minutes.csv) · [graphique](../graphiques/entites_geographiques_minutes/apercu.png)_


### Similarite vocabulaire minutes

20260617 -> 20260729 : Jaccard=0.5209 (vocabulaire moderement renouvele) (648 mots communs / 1244 mots uniques au total), 368 nouveaux, 228 disparus

_Statut **OK** · observation 2026-07-29 · moteur `nlp` · [donnees](../donnees/similarite_vocabulaire_minutes.csv) · [graphique](../graphiques/similarite_vocabulaire_minutes/apercu.png)_


### Lisibilite flesch kincaid

communique (20260916) : Reading Ease=42.1 (0=tres difficile, 100=tres facile), Grade Level=10.5

_Statut **OK** · observation 2026-09-16 · moteur `nlp` · [donnees](../donnees/lisibilite_flesch_kincaid.csv) · [graphique](../graphiques/lisibilite_flesch_kincaid/apercu.png)_


### Frequence mots cles minutes

minutes 20260729, 4717 mots -- mots-cles : {'uncertainty': 8, 'uncertain': 1, 'risks': 6, 'elevated': 17, 'solid': 12, 'strong': 13, 'resilient': 3, 'restrictive': 7} -- theme dominant : 'elevated' (17 mention(s))

_Statut **OK** · observation 2026-07-29 · moteur `nlp` · [donnees](../donnees/frequence_mots_cles_minutes.csv) · [graphique](../graphiques/frequence_mots_cles_minutes/apercu.png)_


### Langage prudence

minutes 20260729 : 74 mots de prudence sur 4780 (15.48 pour mille, langage prudent)

_Statut **OK** · observation 2026-07-29 · moteur `nlp` · [donnees](../donnees/langage_prudence.csv) · [graphique](../graphiques/langage_prudence/apercu.png)_


### Intensite desaccord

minutes 20260729 : 3 dissident(s) au vote, 20 mention(s) de desaccord dans le texte ({'disagreed': 0, 'preferred': 1, 'dissent': 0, 'alternative view': 0, 'some participants': 11, 'a few participants': 6, 'several participants noted': 2}) -- desaccord notable

_Statut **OK** · observation 2026-07-29 · moteur `nlp` · [donnees](../donnees/intensite_desaccord.csv) · [graphique](../graphiques/intensite_desaccord/apercu.png)_

