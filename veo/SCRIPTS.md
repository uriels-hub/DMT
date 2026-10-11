# Les scripts qui fabriquent la page de références

La page publique affirme que rien n'y est écrit à la main : les métadonnées
viennent de l'API NCBI, les comptes sont calculés, les garde-fous tournent à
chaque exécution. Une affirmation pareille se vérifie, et ces fichiers sont ce
par quoi elle se vérifie.

## La chaîne ordinaire

```
page_data.json     groupes thématiques, catégories, PMID
page_autres.json   sources hors PubMed, identifiant stable et lien
        │
        ├── maj.py notices   recharge chaque notice depuis l'API NCBI
        │                    et refuse de se taire sur une divergence
        ├── maj.py liens     ouvre chaque URL hors PubMed
        ├── maj.py page      appelle page.py
        └── maj.py srt       appelle srt.py
                 │
                 └── references_toxicosqueros.html
```

`maj.py` porte les garde-fous, et ils se sont tous déclenchés au moins une fois
sur un défaut réel :

- fins de ligne attendues par extension — CRLF pour les `.srt`, LF ailleurs ;
- jeton de formatage resté dans un libellé, du genre `42 %%` ;
- même étude inscrite deux fois, une fois par son PMID et une fois par son DOI,
  détectée sur le titre normalisé parce qu'un PMID et un DOI ne se ressemblent
  pas ;
- notice sans auteur ou dont le titre commence par « Correction to » : un
  erratum n'est pas une source ;
- notice sans revue, qui signale presque toujours un chapitre d'ouvrage — pour
  ceux-là PubMed renvoie le nom des **éditeurs du livre**, pas celui de l'auteur
  du chapitre, et la page créditerait la mauvaise personne.

`page.py` rend la page. Il échappe tout, puis réadmet nommément cinq balises en
ligne : sans cela les intros affichent `<strong>` en clair, ce qui est arrivé.
Il vérifie en fin de course qu'aucune balise n'est restée échappée et qu'aucun
groupe n'est sans catégorie.

## `outils/` — réutilisables

| Script | Ce qu'il fait |
|---|---|
| `pdftxt.py` | Extrait le texte d'un PDF à flux compressés, sans dépendance. Sert à lire les rapports officiels et les documents que les institutions publient elles-mêmes. |
| `docx.py` | Extrait le texte et la structure d'un `.docx`, titres et listes compris. |
| `audit_page.py` | Croise une liste de références validées ailleurs avec ce que la page contient réellement, et distingue l'absent du mal cherché. |
| `audit.py` | Audite un document : compte les superlatifs, et classe les liens de sa bibliographie selon qu'ils mènent ou non à de la littérature relue par des pairs. |

`audit.py` mérite un mot. Il a été écrit pour examiner un rapport qui affirmait
s'appuyer « exclusivement » sur de la littérature à comité de lecture : il a
compté 97 superlatifs pour 11 324 mots, soit un tous les 116 mots, et trouvé
que 35 % des liens de sa propre bibliographie ne menaient pas à de la
littérature relue. L'outil reste utile contre soi-même.

## `migrations/` — appliquées une fois

Ces scripts ne se relancent pas. Leur résultat est déjà dans `page_data.json`,
et la plupart refuseraient de s'exécuter puisque le groupe qu'ils créent existe
désormais. Ils sont conservés parce qu'ils disent par quoi la donnée est passée.

Dans l'ordre où ils ont été appliqués :

| Script | Ce qu'il a posé |
|---|---|
| `ajout23.py` | « La DMT est-elle un dissociatif ? » et « Takiwasi » |
| `maj_taki.py` | Réécriture de l'intro Takiwasi, une fois le financement français daté |
| `ajout25.py` | « Sérotonine et tonus musculaire » |
| `ajout26.py` | « La consommation répétée » et l'inquiétude valvulaire |
| `categories.py` | Le classement des groupes en cinq catégories |
| `combler1.py` | Cinq notices manquantes et quatre sources juridiques |
| `ajout_radic.py` | « Une atteinte radiculaire » |
| `ajout5.py` | Cinq groupes d'un coup : dose non linéaire, troubles fonctionnels, vision des couleurs, examens, drapeaux rouges |
| `ajout_imao.py` | « Ce que l'IMAO ajoute » |
| `ajout_imao2.py` | « L'IMAO rend dangereux ce qui ne l'était pas » |
| `tableau_ki.py` | Première version du tableau d'affinité — **remplacée**, conservée pour mémoire |
| `tableau_ki2.py` | Le tableau à deux jeux de données, version en service |
| `lecture.py` | Les sept points de lecture posés sous le tableau |
| `sigma1.py` | Les groupes sigma-1 et souvenirs, et la correction d'une phrase réfutée |

`categories.py` illustre à lui seul pourquoi ces fichiers valent d'être gardés.
Il refuse d'écrire si un groupe n'est pas classé ou si un titre cité n'existe
pas — et sa première exécution a échoué sur un **espace insécable** avant un
deux-points, invisible à la lecture. Il compare depuis les titres normalisés.

`tableau_ki.py` est conservé bien qu'il soit faux, et c'est délibéré. Il
opposait les données brutes du criblage NIMH-PDSP à un « tableau en
circulation » présenté comme sans source. Le tableau en question venait d'une
revue à comité de lecture, et `tableau_ki2.py` l'a remplacé par une comparaison
honnête des deux jeux. Une page qui documente ses corrections doit pouvoir
montrer ce qu'elle a corrigé.

Trois migrations portent en tête la mention **non rejouable** : elles lisaient
un fichier de travail transitoire, produit par une recherche vérifiée et
conservé hors du dépôt. Le texte qu'elles ont posé, lui, est dans les données.

## Ce qui n'est pas ici

Les scripts jetables d'une ligne écrits en cours de route, et tout ce qui touche
au film, aux sous-titres ou à la correspondance. Le dépôt public n'est pas leur
place, et `.gitignore` les tient à l'écart.
