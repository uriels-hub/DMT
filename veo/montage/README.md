# Montage TOXICOSQUEROS — état final

18 plans générés, toutes les prises validées à l'oreille.

## Deux versions

| | durée | images |
|---|---|---|
| `TOXICOSQUEROS.mlt` / `_boutabout.mp4` | **141,000 s** | 3384 — plan 18 coupé à 5 s, calé sur la prod |
| `TOXICOSQUEROS_integral.mlt` / `_integral.mp4` | **144,000 s** | 3456 — 18 plans pleins |

Preview 720p de chacune à côté. Listes de concaténation : `liste.txt` et `liste_integrale.txt`.

## Prises retenues

| plan | fichier | pourquoi |
|---|---|---|
| 01 | `montage/01_intro_take3.mp4` | take3 entière, **titre TOXICOSQUEROS incrusté** |
| 03, 06, 07, 15, 18 | `out/XX_take2.mp4` | respelling phonétique |
| 04 | `out/04_take3.mp4` | `chères`, `assois` + voix hors-champ |
| 05, 11, 13 | `out/XX_take2.mp4` | voix hors-champ |
| 12 | `out/12_take3.mp4` | `sciamment` |
| les 7 autres | `out/XX.mp4` | première prise, **encore sans voix** |

## Prononciation : le modele lit en FRANÇAIS

C'est la règle qui commande toutes les autres. Dès que l'amorce dit « in French »,
Veo applique des règles de lecture françaises. Tout respelling à l'anglaise est donc
**contre-productif** : `shairs` pour « chairs » donne n'importe quoi, alors que `chères`
— un mot français réel — donne exactement /ʃɛʁ/.

**Ne réécrire que les mots dont l'orthographe française trahit la prononciation.**
Il n'y en a que deux dans tout le texte :

| mot | écrire | pourquoi |
|---|---|---|
| sciemment | `sciamment` | le `e` s'y prononce /a/, exception du français |
| ayahuasca | `ayawaska` | mot étranger, aucune règle française ne s'applique |

Et deux pièges de mise en forme, indépendants de la langue :

1. **Pas de trait d'union interne.** `ibo-ga` est ressorti « ibagophi ». Écrire `iboga`.
2. **Pas de point-virgule.** Il est parfois vocalisé. Le remplacer par un point.

Les respellings restants dans `prompts.json` (`Rééduke`, `séanss`, `psikologiques`,
`eutanazie`) sont des reliquats inutiles : lus en français ils donnent le bon son, mais
le mot normal aurait suffi. Ne pas les imiter.

`--raw` revient au texte d'origine, champ `dialogue`.

## Voix hors-champ sur le B-roll

Les 11 plans symboliques n'avaient pas de voix : seuls les 7 plans de performance avaient
une ligne au prompt. L'amorce qui marche pour ajouter la voix sans faire entrer de personnage :

> A man's voice raps in French off-screen over the shot, no speaker visible, nobody enters frame

Testé sur 04, 05, 11, 13 — les quatre lignes les plus dures du texte. **Aucun refus du filtre**,
et aucun rappeur ne s'invite dans le cadre. Restent 7 plans à faire : 02, 08, 09, 10, 14, 16, 17.

## Synchro image/son

Les fichiers Veo ont une vidéo de 8,000 s pour un audio de 7,936 s. À la concaténation,
l'encodeur AAC ajoute son amorçage de 1024 échantillons, soit **21,33 ms** de décalage
constant — mesuré à +21,4 ms sur les 18 plans, sans dérive. Compensation :

```bash
-af "atrim=start=0.021333,asetpts=PTS-STARTPTS"
```

Vérifié après coup : 0,0 ms sur les 18 plans.

## Re-rendre après une reprise

```bash
"C:/Program Files/Shotcut/ffmpeg.exe" -f concat -safe 0 -i liste.txt -an -frames:v 3384 -c:v libx264 -crf 20 -preset veryfast -pix_fmt yuv420p -r 24 -y TOXICOSQUEROS_boutabout.mp4
```

`-frames:v` n'est pas cosmétique : sans lui le démuxeur concat sort 141,25 s (et 144,04 s
pour l'intégrale, avec `-frames:v 3456`).

Régénérer le projet MLT : voir la boucle dans l'historique, en substance
`melt -profile atsc_1080p_24 <fichiers> audio_index=-1 -consumer xml:projet.mlt`.
**Ne jamais lancer `melt ... -consumer null:` sans `terminate_on_pause=1`** — le processus
reste en pause à la fin de la timeline et ne se termine jamais.

## Reste à faire

- caler sur l'acapella réelle (le découpage suppose 4,51 syll/s)
- logo AMS sur le plan 06
- décider : compteur numérique en bas à droite du plan 14 (tombe pile sur « calcule la somme »),
  texte inventé « ROINEK » sur la banderole du plan 04
- le plan 18 ne raccorde pas avec le casting des 5 personnages — limite de Lite, qui ne prend
  ni images de référence ni plus d'une première frame

## Carton de fin « mot d'ordre » (ajout)

`carton_cri.py` fabrique un carton de 4 s et l'ajoute au film :
**150,000 s → 154,000 s**, 3696 images. Sans `--go` il ne colle rien.

Le film d'origine n'est jamais touché : la concaténation se fait en copie de flux
et la version longue s'appelle `TOXICOSQUEROS_final_cri.mp4`. La synchro son du
montage, mesurée et corrigée des 21,33 ms d'amorçage AAC, reste intacte.

Trois choses apprises en le fabriquant :

1. **Ne pas spécifier de police.** Le défaut de `melt` est exactement celui du
   carton du refrain. En imposer une casse l'accord entre les deux.
2. **Jamais `-frames:v` quand il y a une piste son.** ffmpeg clôture la sortie dès
   que le compte d'images est atteint, et le silence reste tronqué à une
   demi-seconde — un trou de son à la jonction, qu'on ne voit pas passer tant
   qu'on n'a pas regardé le film jusqu'au bout. `-t` borne proprement les deux flux.
   Le script contrôle désormais images et son avant de laisser coller.
3. **Veo ne sait pas écrire.** Voir `../catalogue_videos.md` : le carton
   d'avertissement généré par le modèle rend « Even a small *amont* of *ąahuea*
   can endanger life and *case lasleg harp* ». Tout texte à l'écran se compose
   hors du modèle.

Les 9 sous-titres portent le mot d'ordre à 150,5–153,5 s, dans leur langue.

## Masterisation pour YouTube

Mesuré sur `TOXICOSQUEROS_final_cri.mp4` : **-16,3 LUFS** intégré et crête vraie
à **+0,1 dBFS**. Deux défauts distincts.

La crête au-dessus de 0 dBFS est un vrai défaut : les pics inter-échantillons
distordent au transcodage en AAC et en Opus, que YouTube fait systématiquement.
Et -16,3 LUFS est deux décibels sous la cible de la plateforme, qui baisse les
pistes trop fortes mais ne remonte jamais les trop faibles : le morceau aurait
sonné plus faible que les vidéos voisines.

`TOXICOSQUEROS_master.mp4` : **-14,0 LUFS, crête -0,7 dBFS**, loudnorm en deux
passes. Le flux vidéo est **copié sans réencodage** — même MD5 que la source,
3696 images, 154,000 s. Seul l'audio a été refait, en AAC 256 kb/s.

```bash
# passe 1 : mesurer
ffmpeg -i TOXICOSQUEROS_final_cri.mp4 -map 0:a:0 \
  -af loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json -f null -
# passe 2 : appliquer, en reportant les valeurs mesurees
ffmpeg -i TOXICOSQUEROS_final_cri.mp4 -map 0:v:0 -c:v copy -map 0:a:0 \
  -af loudnorm=I=-14:TP=-1.0:LRA=11:measured_I=...:linear=true \
  -c:a aac -b:a 256k -movflags +faststart TOXICOSQUEROS_master.mp4
```

**C'est ce fichier qu'il faut mettre en ligne.**
