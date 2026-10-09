#!/usr/bin/env python3
"""Fabrique les SRT de TOXICOSQUEROS, une langue par fichier <code>.json.

    .venv/Scripts/python.exe srt.py            # toutes les langues trouvees
    .venv/Scripts/python.exe srt.py es pt      # seulement celles-la

Le francais vient de prompts.json (champ `dialogue`), les autres de <code>.json
avec les cles "01".."18" et "outro". Le minutage est commun : chaque plan occupe
sa fenetre de 8 s et le texte s'y repartit au prorata des caracteres.
"""
import io
import json
import pathlib
import re
import sys

MAXL, MINS, FEN = 42, 1.3, 8.0
NB = u" "          # insecable : garde la ponctuation double collee au mot
ICI = pathlib.Path(__file__).resolve().parent
DEST = ICI.parent
OUTRO = (144.5, 149.5)
# Le carton « mot d'ordre » occupe 150,000 a 154,000 s, fondus de 4 images compris.
# Le sous-titre se tient a l'interieur, hors des fondus.
CRI = (150.5, 153.5)
# Le carton d'avertissement ouvre le film et pousse tout le reste de 4 s.
# Le decalage s'applique a l'ecriture, pas au calcul : les fenetres de 8 s
# restent lisibles telles quelles dans le code.
DECALAGE = 4.0
CRI_FR = u"Non aux rituels d’intoxication imposés par des proches !"


def prep(t):
    return re.sub(r"\s+([;:!?])", NB + r"\1", t.strip())


def plier(bloc):
    """Retour a la ligne glouton : aucune ligne ne depasse MAXL."""
    lignes, cur = [], ""
    for mot in bloc.split(" "):
        essai = (cur + " " + mot).strip() if cur else mot
        if len(essai) > MAXL and cur:
            lignes.append(cur)
            cur = mot
        else:
            cur = essai
    if cur:
        lignes.append(cur)
    return "\n".join(lignes)


def decouper(texte):
    """Blocs coupes sur ponctuation forte, jamais plus courts que MINS secondes."""
    mini = max(14, int(len(texte) * MINS / FEN))
    blocs, cur = [], ""
    for mot in texte.split(" "):
        essai = (cur + " " + mot).strip() if cur else mot
        if len(essai) > MAXL * 3:
            blocs.append(cur)
            cur = mot
        else:
            cur = essai
            if re.search(u"[.;:!?]$", mot) and len(cur) >= mini:
                blocs.append(cur)
                cur = ""
    if cur:
        blocs.append(cur)
    i = 0
    while i < len(blocs):          # absorbe les blocs trop brefs dans leur voisin
        if len(blocs) > 1 and len(blocs[i]) < mini:
            j = i - 1 if i else 1
            a, b = min(i, j), max(i, j)
            blocs[a:b + 1] = [(blocs[a] + " " + blocs[b]).strip()]
            i = 0
        else:
            i += 1
    return blocs


def tc(s):
    h, r = divmod(s, 3600)
    m, r = divmod(r, 60)
    sec = int(r)
    return "%02d:%02d:%02d,%03d" % (h, m, sec, round((r - sec) * 1000))


def fabriquer(code, textes, outro, cri):
    cues = []
    for i in range(1, 19):
        t = prep(textes.get("%02d" % i, ""))
        if not t:
            continue
        blocs = decouper(t)
        poids = [len(b) for b in blocs]
        total = sum(poids)
        debut = (i - 1) * FEN
        for b, p in zip(blocs, poids):
            duree = FEN * p / total
            cues.append((debut, debut + duree - 0.08, plier(b)))
            debut += duree
    cues.append((OUTRO[0], OUTRO[1], plier(prep(outro))))
    if cri:
        cues.append((CRI[0], CRI[1], plier(prep(cri))))

    srt = "\n".join("%d\n%s --> %s\n%s\n"
                    % (n, tc(a + DECALAGE), tc(b + DECALAGE), c)
                    for n, (a, b, c) in enumerate(cues, 1))
    chemin = DEST / ("TOXICOSQUEROS.%s.srt" % code)
    # SubRip veut CRLF et un dernier bloc suivi d'une ligne vide. On l'ecrit
    # explicitement : en mode texte Python traduirait selon l'OS, pas selon la norme.
    with io.open(str(chemin), "w", encoding="utf-8", newline="\r\n") as f:
        f.write(srt + "\n")

    lignes = [l for bl in srt.split("\n\n") for l in bl.split("\n")[2:]]
    trop = sum(1 for l in lignes if len(l) > MAXL)
    orph = sum(1 for l in lignes if re.match(u"^[,;:.!?]+$", l.strip()))
    duree = [b - a for a, b, _ in cues]
    print("  %-5s %2d blocs  %.2f-%.2f s  lignes>%d:%d  orphelins:%d"
          % (code, len(cues), min(duree), max(duree), MAXL, trop, orph))


def main():
    voulues = sys.argv[1:]

    fr = {s["id"]: s.get("dialogue", "")
          for s in json.loads((ICI / "prompts.json").read_text(encoding="utf-8"))["shots"]}
    langues = {"fr": (fr, u"Gourou du malheur, prêche le mal et pêche, "
                          u"le mécréant au détriment des pénitents", CRI_FR)}

    for f in sorted(ICI.glob("??.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if "outro" in d:
            langues[f.stem] = (d, d["outro"], d.get("cri", ""))

    print("TOXICOSQUEROS - sous-titres")
    for code in sorted(langues):
        if voulues and code not in voulues:
            continue
        textes, outro, cri = langues[code]
        fabriquer(code, textes, outro, cri)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()
