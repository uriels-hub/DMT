# Veo 3.1 Lite — config Gemini API pour TOXICOSQUEROS

## Modèle

`veo-3.1-lite-generate-preview` — c'est le nom exact du tier « Lite ».
Il n'existe pas de « Veo 3 Lite » : le Lite n'est apparu qu'avec la génération 3.1.

| | |
|---|---|
| Entrées | texte, image (première et dernière frame) |
| Sortie | 1 vidéo, **avec audio** |
| Résolutions | 720p, 1080p — **pas de 4K** |
| Durées | 4, 6, 8 s — **8 s uniquement en 1080p** |
| Ratios | 16:9, 9:16 |
| Prompt | 1 024 tokens max |
| Images de référence | **non supportées** (réservées à 3.1 et 3.1 Fast) |
| Extension de vidéo | non supportée |
| Rétention serveur | 2 jours, après quoi le fichier est supprimé |

## Tarif

| Modèle | 720p | 1080p | 4K |
|---|---|---|---|
| `veo-3.1-generate-preview` | 0,40 $/s | 0,40 $/s | 0,60 $/s |
| `veo-3.1-fast-generate-preview` | 0,10 $/s | 0,12 $/s | 0,30 $/s |
| **`veo-3.1-lite-generate-preview`** | **0,05 $/s** | **0,08 $/s** | — |

Le découpage fait 18 plans × 8 s = 144 s. En 8 s on est forcé en 1080p, donc
**144 × 0,08 = 11,52 $ la passe complète**. Compte 25-35 $ avec les reprises.

## Les deux contraintes qui changent le plan de travail

**1. Le Lite ne prend pas les images de référence.** La cohérence des visages passe donc par
la **première frame** : `--first_frame` sur un still de `_REF_PERSOS/`, et Veo part de cette
image exacte. C'est plus rigide (ça impose le cadre d'ouverture du plan) mais ça marche sur
les plans 03, 07, 12 et 15, où le personnage est déjà en place au premier photogramme.

Les plans 01, 06 et 18 n'en prennent pas : 01 doit ouvrir sur le décor vide, 06 et 18 sont
des plans de groupe qu'aucun still ne couvre. Pour ceux-là, la description textuelle du
personnage dans le prompt est la seule accroche.

Si la cohérence ne tient pas, le vrai correctif est de passer ces plans en
`veo-3.1-fast-generate-preview` (0,12 $/s en 1080p), qui accepte jusqu'à 3 images de référence.
7 plans de performance en Fast = 56 s × 0,12 = 6,72 $, le reste en Lite.

**2. 8 s impose le 1080p.** Pas de découpage 8 s en 720p à 0,05 $/s. Le 1080p tombe bien :
tes 5 clips existants sont déjà en 1920×1080.

## Installation

Déjà fait : venv Python 3.13.1 dans `veo/.venv`, `google-genai 2.24.0` installé.
`requirements.txt` est gelé, `.gitignore` exclut `.venv/` et `out/`.

Pour le refaire ailleurs :

```bash
py -3.13 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

**Veo n'existe pas en tier gratuit.** Les trois modèles Veo 3.1 sont marqués « Not available »
dans la colonne free tier. Il faut la facturation activée sur le projet lié à la clé, sinon
l'API répond `429 RESOURCE_EXHAUSTED` quelle que soit la requête.
État du quota : https://ai.dev/rate-limit

Il reste la clé API, à prendre sur https://aistudio.google.com/apikey :

```bash
setx GEMINI_API_KEY "ta_cle"
```

Le SDK lit `GEMINI_API_KEY` tout seul, `genai.Client()` sans argument.
Rouvre le terminal après `setx` — `setx` n'affecte pas la session en cours.

## Utilisation

Appelle le python du venv directement, pas besoin d'activer :

```bash
.venv/Scripts/python.exe generate.py --dry-run     # prompts assemblés + coût, aucun appel
.venv/Scripts/python.exe generate.py               # génère tout dans out/
.venv/Scripts/python.exe generate.py --only 03 07  # seulement ces plans
.venv/Scripts/python.exe generate.py --take 2      # 2e prise -> out/03_take2.mp4
.venv/Scripts/python.exe generate.py --no-audio    # sans piste audio
```

Si tu préfères activer le venv : `.venv\Scripts\activate` en PowerShell, puis `python generate.py`.

Le script :

- reprend où il s'est arrêté (un plan déjà dans `out/` est sauté) ;
- garde le nom de l'opération dans `out/.ops/` pour reprendre le polling après un crash,
  sans repayer la génération ;
- **retente automatiquement sans la ligne chantée** quand le filtre refuse un prompt —
  c'est le cas de figure prévu dans la shotlist, tu gardes le jeu et tu perds le lipsync ;
- tourne 3 générations en parallèle (`--workers`).

`person_generation` est sur `allow_adult` par défaut. Si tu veux `allow_all` et que l'API te
le refuse depuis la France, reste sur `allow_adult` : ça ne change rien ici, il n'y a aucun
mineur dans le découpage.

## Paramètres : deux couches de refus

Le SDK et le modèle filtrent séparément, et la doc ne documente ni l'un ni l'autre.

**Refusés par le SDK en mode Developer API** (réservés à Vertex / Enterprise) :
`seed`, `fps`, `generate_audio`, `mask`, `compression_quality`, `output_gcs_uri`, `pubsub_topic`.
Il n'y a donc pas moyen de générer sans piste audio avec une clé `GEMINI_API_KEY`.

**Refusé par `veo-3.1-lite` lui-même** : `negative_prompt` → 400
« `negativePrompt` isn't supported by this model ». Il est resté dans le script derrière
`--negative`, utilisable si tu passes en `veo-3.1` ou `veo-3.1-fast`.

En Lite, la protection contre les sous-titres incrustés repose donc seulement sur la fin du
suffixe (« No on-screen text, no subtitles, no captions »). Si Veo les brûle quand même dans
l'image, c'est un argument de plus pour mettre les 7 plans de dialogue en 3.1 Fast.

**Accepté et utilisé** : `aspect_ratio`, `resolution`, `duration_seconds`, `person_generation`.

**Première frame** : il faut un `types.Image` (`types.Image.from_file`), pas un `File` renvoyé
par `client.files.upload()` — avec un File le SDK signale un type mismatch mais n'echoue pas,
et l'image part à la poubelle sans rien dire.

## Après génération

`out/18.mp4` est généré en 8 s et se coupe à 5 s au montage — c'est le seul plan à trimmer.
Total monté : 141 s.

Et coupe l'audio Veo partout : il est a cappella, sans beat, quasi mono.
