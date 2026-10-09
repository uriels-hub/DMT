# Catalogue des rushes Veo — `_VIDEOS/`

Relevé du 9 octobre 2026. 40 fichiers vidéo, 399 Mo, dossier `_VIDEOS/` (hors dépôt).

**Toutes les vidéos ont exactement 8,00 s et 24 ips, H.264 + AAC stéréo 48 kHz.**
C'est la signature de Veo : aucune n'a été étendue ni remontée. Deux résolutions
seulement, 1920×1080 et 1280×720, plus un format vertical isolé.

Les fichiers sont nommés `<identifiant de génération>_sample_<0..3>.mp4` : chaque
identifiant est une requête, chaque `sample` une des quatre propositions rendues
par le modèle pour cette même requête. Les `téléchargement*.mp4` et `who_*.mp4`
ont été renommés à la main et ont perdu cette trace.

## Quatre projets, pas un

| lot | n | déf. | sujet |
|---|---|---|---|
| `14275034601060109446` | 4 | 1080p | **TOXICOSQUEROS** — performance, friches industrielles, micro vintage |
| `1433611169484098437` | 4 | 1080p | **TOXICOSQUEROS** — performance, lianes et chaînes, lumière verte |
| `2719149923042343045` | 4 | 1080p | **TOXICOSQUEROS** — performance, hangar, néons violets |
| `4210923735309622021` | 4 | 1080p | **TOXICOSQUEROS** — performance ; un plan porte « S-C-H-O-E-T-T-E-L » incrusté |
| `9914064800409589354` | 4 | 1080p | **TOXICOSQUEROS** — performance, quatre personnages face caméra |
| `téléchargement*.mp4` | 4 | 720p | **Ayahuasca** — scènes rituelles, visages en détresse, carton d'avertissement |
| `15341046903362853382` | 4 | 720p | *Noël* — chorale de lutins, cloches |
| `3658156946020780624` | 4 | 720p | *Noël / Cthulhu* — père Noël tentaculaire, cartons « Ia-ia-Christmas fhtagn! » |
| `4761372095888930937` | 3 | 720p | *Cthulhu* — cathédrale, grimoire, silhouettes en procession |
| `who_*.mp4` | 4 | 720p | *Bonne année* — TARDIS en vortex, animation peinte |
| `Vidéo_Générée_Roots_Rouste.mp4` | 1 | 720×1280 | *ROOTS 2 ROUSTE* — affiche animée verticale, soirée ragga jungle |

Vingt clips sur quarante relèvent de TOXICOSQUEROS. Le reste appartient à trois
projets sans rapport, dont un projet Kdenlive à part, `ROOTS2ROUSTE.kdenlive`.

## Ce que ce relevé a trouvé, et qui compte

### Veo ne sait pas écrire

Le carton d'avertissement de la série `téléchargement` devait dire *« Even a small
amount of ayahuasca can endanger life and cause lasting harm »*. Il affiche :

> Even a small **amont** of **ąahuea** can endanger life and **case lasleg harp**.

Quatre mots sur treize sont détruits, dont le nom de la substance. Les cartons
« Ia-ia-Christmas fhtagn! » du lot Cthulhu s'en tirent mieux, mais un seul
caractère faux suffit à ruiner un carton d'avertissement.

**Conséquence pratique :** ne jamais demander un texte à Veo. Le carton de fin de
TOXICOSQUEROS est composé après coup, hors du modèle, par `montage/carton_cri.py` —
c'est la bonne méthode, et il faut s'y tenir pour tout texte à l'écran.

Le plan portant « S-C-H-O-E-T-T-E-L » est l'exception qui confirme : le mot est
juste, mais c'est un coup de chance sur une chaîne courte et espacée.

### Trois points à régler avant toute diffusion

1. **Le TARDIS** de la série `who_` est une marque et un décor protégés de la BBC.
   Un vœu de bonne année diffusé en privé ne pose pas de problème ; une mise en
   ligne publique, si.
2. **L'affiche ROOTS 2 ROUSTE** nomme deux personnes réelles, « CLOVIS LA MALICE »
   et « FRISCOU ». Leur accord est nécessaire avant publication.
3. **La série `téléchargement`** montre des visages jeunes en détresse dans un
   cadre rituel. Le sujet est exactement celui du morceau, et c'est précisément ce
   qui rend ces plans délicats sur une plateforme publique : l'apparence de minorité
   combinée à la détresse déclenche les filtres, et le propos se perd dans le litige.
   À arbitrer plan par plan, pas en bloc.

### Deux lots sont des doublons de casting

Les cinq lots TOXICOSQUEROS proposent chacun quatre interprètes différents pour la
même requête. Aucun personnage ne revient d'un lot à l'autre : c'est la limite déjà
connue de Veo Lite, qui n'accepte ni image de référence ni cohérence de casting
entre deux requêtes. C'est la même cause que le défaut de raccord du plan 18 du
montage, noté dans `montage/README.md`.
