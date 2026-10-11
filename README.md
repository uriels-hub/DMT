# TOXICOSQUEROS

Clip de rap français contre le néo-chamanisme, l'usage abusif d'ayahuasca et d'iboga,
la dérive sectaire, et l'administration de ces substances à des enfants par leurs proches.

**Non aux rituels d'intoxication imposés par des proches !**

Texte et interprétation : Uriel Schœttel - Longuet — SOUFFLE, AMS crew.
Images et voix générées par Google Veo 3.1 : aucun interprète n'est une personne réelle,
aucun lieu n'existe. Seuls les textes sont de l'auteur.

Film : un carton d'avertissement, 18 plans de 8 s, un carton de refrain,
un carton de mot d'ordre, un carton de ressources. **163,000 s.**
Neuf pistes de sous-titres, décalées de 4 s pour le carton de tête.

La vidéo :
https://youtu.be/AwKytfBl_w8

Le film et les neuf pistes de sous-titres :
https://github.com/uriels-hub/DMT/releases/tag/v1.0

Les **423 sources** sur lesquelles le morceau s'appuie, chacune cliquable :
https://claude.ai/artifact/WWVKdfGfPUVbCN6Q2Xr6NC

Comment le texte se découpe dans le temps, vers par vers :
https://claude.ai/artifact/A1qH5m4mUQthSW9jA7cMuP

## Ce que contient ce dépôt

Le code et les textes. **Pas les médias** : 2,1 Go de rushes et de montages
restent dehors, dont trois fichiers au-delà de la limite de 100 Mo par fichier
de GitHub.

Le film fini, lui, est publié en *release* : un asset accepte jusqu'à 2 Go et ne
compte pas dans le poids du dépôt.

| | |
|---|---|
| `paroles/TOXICOSQUEROS.original.fr.txt` | **l'original. Fait foi.** |
| `paroles/TOXICOSQUEROS.original.en.txt` | version anglaise de l'auteur |
| `paroles/README.md` | ce que chaque graphie et chaque émoji font au temps |
| `paroles_TOXICOSQUEROS.txt` | version de lecture, dérivée de l'original |
| `youtube_TOXICOSQUEROS.md` | description YouTube, liens vérifiés un par un |
| `youtube_NOVID.md` | description de SUJET DE LA PRÉCIPITATION, version son |
| `TOXICOSQUEROS.<langue>.srt` | sous-titres : fr, en, es, pt, de, it, nl, ru, uk |
| `veo/prompts.json` | les 18 plans : scène, dialogue, première image, style |
| `veo/page_data.json`, `veo/page_autres.json` | les sources, par catégorie et par thème |
| `veo/references_toxicosqueros.html` | la page publique de références, générée |
| `veo/temps_data.json`, `veo/temps_toxicosqueros.html` | la partition : vers, syllabes, débit |
| `veo/prononciation.json` | ce que chaque graphie devient pour une synthèse vocale |
| `veo/SCRIPTS.md` | la chaîne de fabrication de la page, et ses garde-fous |
| `veo/montage/*.mlt` | projets Kdenlive/MLT |

## Les programmes

```bash
veo/generate.py        # genere les plans avec Veo 3.1, reprenable, cout affiche
veo/chain_shot.py      # etend un plan au-dela de 8 s (lite ne sait pas etendre)
veo/srt.py             # fabrique les 9 SRT depuis prompts.json et les <langue>.json
veo/page.py            # genere la page de references
veo/maj.py             # recharge PubMed, regenere page et sous-titres, controle tout
veo/temps.py           # mesure le texte note et fabrique la page de partition
veo/dire.py            # fait dire le texte par Piper, plan par plan, et mesure
veo/youtube_srt.py     # televerse les 9 pistes de sous-titres via l'API YouTube
veo/montage/carton_cri.py  # fabrique le carton de fin et rallonge le film
veo/outils/            # outils reutilisables : lecture de PDF et de docx, audits
veo/migrations/        # scripts appliques une fois, conserves comme trace
```

`veo/SCRIPTS.md` détaille la chaîne et les quatorze migrations.

## La page de références

**423 sources** : 391 notices PubMed réparties en 36 groupes, et 32 sources hors
PubMed — décisions de justice, rapports publics, travaux sans identifiant PubMed.
Les groupes sont rangés en cinq catégories, du mécanisme vers le discours :

| Catégorie | Groupes | Références |
|---|---:|---:|
| Pharmacologie et mécanismes | 12 | 173 |
| Clinique et séquelles | 8 | 59 |
| Ce que les examens trouvent | 6 | 65 |
| Épidémiologie et valeur de la preuve | 2 | 15 |
| Emprise, discours et dérive | 8 | 79 |

Rien n'est écrit à la main dans la bibliographie : les métadonnées des notices
PubMed viennent de l'API NCBI E-utilities et sont rechargées à chaque exécution
de `maj.py`. Une erreur possible est une erreur de programme, pas une invention.

`maj.py` porte des garde-fous qui se sont tous déclenchés au moins une fois sur
un défaut réel : fins de ligne attendues par extension, jeton de formatage resté
dans un libellé, même étude inscrite deux fois sous son PMID et sous son DOI,
notice sans auteur ou intitulée « Correction to » — un erratum n'est pas une
source —, notice sans revue qui trahit un chapitre d'ouvrage dont PubMed
attribue la paternité aux éditeurs du livre, et décompte des sources annoncé par
ce fichier.

La page sépare partout trois niveaux : ce qui est établi, ce qui est un mécanisme
plausible, et ce qui n'est pas établi. Les absences y sont écrites en capitales,
parce qu'une absence constatée vaut autant qu'une présence et protège la page.
Elle porte aussi, délibérément, des travaux qui contredisent d'autres travaux
qu'elle cite.

## Les paroles ne se corrigent pas

Dans `paroles/`, les graphies et les émojis de l'original sont **de la
notation** : des notes et des silences, qui altèrent le temps. `Go~uu~urou`,
`&spoir`, `Sscrupules`, `dDôgmes`, `v€rgogn€`, les émojis en fin de vers :
rien n'est une faute. Un correcteur orthographique détruirait le texte, une
relecture bien intentionnée aussi. Détail dans `paroles/README.md`.

## Deux conventions à ne pas défaire

**Fins de ligne.** CRLF pour les `.srt`, c'est la norme SubRip et les lecteurs les
plus stricts n'acceptent que ça ; LF partout ailleurs. `.gitattributes` l'impose,
et `maj.py` le vérifie à chaque exécution.

**Prononciation.** Veo lit le texte *en français*. Tout respelling à l'anglaise est
donc contre-productif : `shairs` pour « chairs » donne n'importe quoi, `chères` donne
exactement le bon son. Ne réécrire que les mots dont l'orthographe française trahit
la prononciation — il n'y en a que deux dans tout le texte. Détail dans
`veo/montage/README.md`.

## Ce qui n'est pas ici

Les identifiants (`veo/.env`, `client_secret.json`), les médias, et les documents
de travail privés — correspondance, notes nominatives, `.docx`, PDF. Voir
`.gitignore`.

## Signaler

Dérive sectaire en France : MIVILUDES.
Accompagnement des victimes et des familles : CCMM, UNADFI.

## Licence

`LICENSE` porte la licence MIT, **et elle ne couvre que le code** : les programmes
Python, les scripts de montage, les fichiers de configuration.

Elle ne couvre pas l'œuvre. Les paroles, les neuf pistes de sous-titres et leurs
traductions, le film et la page de références restent la propriété de l'auteur,
tous droits réservés. Une licence logicielle appliquée sans précaution à un dépôt
qui contient un texte autoriserait n'importe qui à le reprendre : la distinction
est écrite en toutes lettres dans le fichier.
