#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mesure les temps du texte original et fabrique la page de partition.

    .venv/Scripts/python.exe temps.py          # mesure, et ecrit la page
    .venv/Scripts/python.exe temps.py --table  # mesure seulement, a l'ecran

Entrees   paroles/TOXICOSQUEROS.original.fr.txt   le texte note, qui fait foi
          paroles/TOXICOSQUEROS.original.en.txt   la version anglaise
          temps_gabarit.html                      le gabarit de la page
Sorties   temps_data.json                         les mesures
          temps_toxicosqueros.html                la page

CE QUE CETTE MESURE VAUT, ET CE QU'ELLE NE VAUT PAS

Les syllabes sont comptees par groupes voyelliques avec elision du e muet final.
C'est une approximation reconnue comme telle. Surtout, elle compte le texte TEL
QU'ECRIT : « Go~uu~urou » vaut ce que valent ses lettres, pas ce que vaut son
allongement. La notation echappe par nature au comptage, et c'est precisement
pour cela qu'elle existe.

Le decoupage en dix-huit plans est CALCULE, pas releve sur la bande. Avec
soixante-six vers chantes et des groupes de trois ou quatre, l'arithmetique
n'admet qu'une solution : douze plans de quatre vers et six de trois. Parmi
les decoupages possibles, on retient celui qui egalise le mieux le debit.
"""
import html
import io
import json
import pathlib
import re
import sys

ICI = pathlib.Path(__file__).resolve().parent
PAR = ICI.parent / "paroles"
VOY = u"aeiouy\u00e0\u00e2\u00e4\u00e9\u00e8\u00ea\u00eb\u00ee\u00ef\u00f4\u00f6\u00f9\u00fb\u00fc\u00ff\u0153"
EMO = re.compile(u"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")
CAPS = re.compile(u"\\b[A-Z\u00c0\u00c9\u00ca\u0152]{2,}\\b")
PLANS, FENETRE, DEBUT = 18, 8, 4      # 18 plans de 8 s, apres le carton de tete


def syl_fr(v):
    n = 0
    for m in re.findall(u"[a-zA-Z" + VOY + u"\u00e7'\u2019-]+", v.lower()):
        c = len(re.findall(u"[" + VOY + u"]+", m.replace(u"\u2019", u"'")))
        if c > 1 and m.endswith(u"e") and not m.endswith((u"\u00e9e", u"ie")):
            c -= 1
        if m.strip(u"'-"):
            n += max(c, 1)
    return n


def syl_en(v):
    n = 0
    for m in re.findall(u"[a-zA-Z'\u2019-]+", v.lower()):
        m = m.replace(u"\u2019", u"'")
        c = len(re.findall(u"[aeiouy]+", m))
        if c > 1 and m.endswith(u"e") and not m.endswith((u"le", u"ee", u"ye")):
            c -= 1
        if m.endswith(u"le") and len(m) > 2 and m[-3] not in u"aeiouy":
            c += 1
        if m.strip(u"'-"):
            n += max(c, 1)
    return n


# CE QUI COMPTE COMME NOTATION, ET POURQUOI CE PERIMETRE
#
# Seules comptent les graphies qui n'appartiennent pas a l'orthographe fran\u00e7aise
# ordinaire, plus les emoji. La ponctuation courante \u2014 deux-points, point-virgule,
# parentheses, guillemets \u2014 en est exclue : elle existe dans n'importe quel texte
# et l'inclure diluerait la mesure jusqu'a ne plus rien dire. Trois perimetres ont
# ete compares sur ce texte :
#   emoji seuls                        9 vers   14,9 syl contre 9,5   +56 %
#   emoji + graphies non standard     20 vers   13,8 syl contre 8,7   +58 %   <- retenu
#   le precedent + la ponctuation     27 vers   13,0 syl contre 8,4   +54 %
# Le perimetre retenu est le plus large qui reste defendable : chaque marque y est
# un signe que l'auteur a ecrit expres, et qu'un correcteur effacerait.
MIN, MAJ = u"a-z\u00e0-\u00ff", u"A-Z\u00c0-\u00dd\u0152"
GRAPHIES = [
    (u"~", u"allongement"),
    (u"\\+\\+\\+", u"insistance"),
    (u"[\u20ac$]", u"substitution"),
    (u"\\\\", u"coupure"),
    (u"&[%s]" % MIN, u"elision ecrite"),
    (u"[%s][%s]" % (MIN, MAJ), u"capitale interne"),
    (u"\\b([A-Za-z])\\1(?=[%s])" % MIN, u"attaque doublee"),
    (u'[%s]"' % MIN, u"guillemet orphelin"),
]


def marques(v):
    out = []
    for motif, role in GRAPHIES:
        m = re.search(motif, v)
        if m:
            out.append((m.group(0), role))
    out += [(x, u"silence") for x in EMO.findall(v)]
    return out


def lire(nom):
    """Les vers non vides. La premiere ligne est une en-tete, pas un vers."""
    t = (PAR / nom).read_text(encoding="utf-8").split(u"\n")
    v = [x for x in t if x.strip()]
    return v[0], v[1:]


def decouper(s):
    """Groupes de 3 ou 4 vers, PLANS groupes, debit le plus egal possible."""
    n, cible, inf = len(s), sum(s) / float(PLANS), float("inf")
    d = [[inf] * (PLANS + 1) for _ in range(n + 1)]
    ch = [[None] * (PLANS + 1) for _ in range(n + 1)]
    d[0][0] = 0.0
    for i in range(n + 1):
        for k in range(PLANS + 1):
            if d[i][k] == inf:
                continue
            for t in (3, 4):
                j, k2 = i + t, k + 1
                if j > n or k2 > PLANS:
                    continue
                c = d[i][k] + (sum(s[i:j]) - cible) ** 2
                if c < d[j][k2]:
                    d[j][k2], ch[j][k2] = c, (i, t)
    if d[n][PLANS] == inf:
        sys.exit("aucun decoupage en %d groupes de 3 ou 4 vers pour %d vers"
                 % (PLANS, n))
    out, i, k = [], n, PLANS
    while k:
        i0, _ = ch[i][k]
        out.append((i0, i))
        i, k = i0, k - 1
    out.reverse()
    return out


def mesurer():
    tfr, fr = lire("TOXICOSQUEROS.original.fr.txt")
    ten, en = lire("TOXICOSQUEROS.original.en.txt")
    if len(fr) != len(en):
        sys.exit("les deux versions n'ont pas le meme nombre de vers : %d et %d"
                 % (len(fr), len(en)))
    s = [syl_fr(v) for v in fr]
    se = [syl_en(v) for v in en]
    cuts = decouper(s)
    plans = [{"n": i + 1, "t0": DEBUT + i * FENETRE, "t1": DEBUT + (i + 1) * FENETRE,
              "a": a, "b": b, "syl": sum(s[a:b]), "syl_en": sum(se[a:b]),
              "debit": round(sum(s[a:b]) / float(FENETRE), 2), "nvers": b - a}
             for i, (a, b) in enumerate(cuts)]
    vers = []
    for i, (f, g) in enumerate(zip(fr, en)):
        p = next(x for x in plans if x["a"] <= i < x["b"])
        vers.append({"i": i + 2, "fr": f, "en": g, "sfr": s[i], "sen": se[i],
                     "plan": p["n"], "rang": i - p["a"] + 1,
                     "m": [{"s": a_, "r": b_} for a_, b_ in marques(f)]})
    notes = [v for v in vers if v["m"]]
    nus = [v for v in vers if not v["m"]]
    return {"entete": {"fr": tfr, "en": ten}, "plans": plans, "vers": vers,
            "tot": {"fr": sum(s), "en": sum(se), "n": len(fr),
                    "notes": len(notes),
                    "moy_note": round(sum(v["sfr"] for v in notes) / float(len(notes)), 1),
                    "moy_nu": round(sum(v["sfr"] for v in nus) / float(len(nus)), 1)}}


def page(d):
    e, P, V, T = html.escape, d["plans"], d["vers"], d["tot"]
    mx = max(p["debit"] for p in P)
    L = []
    for p in P:
        L.append(u'<tr class="p"><th colspan="5" scope="rowgroup">'
                 u'<span class="pn">plan %d</span><span class="pt">%d\u2013%d\u202fs</span>'
                 u'<span class="pv">%d vers</span>'
                 u'<span class="pd"><i style="--h:%.0f%%"></i>%.2f syl/s</span>'
                 u'<span class="ps">%d syllabes</span></th></tr>'
                 % (p["n"], p["t0"], p["t1"], p["nvers"],
                    100.0 * p["debit"] / mx, p["debit"], p["syl"]))
        for v in [x for x in V if x["plan"] == p["n"]]:
            m = u"".join(u'<b class="m" title="%s">%s</b>' % (e(x["r"]), e(x["s"]))
                         for x in v["m"])
            L.append(u'<tr%s><td class="i">%d</td><td class="fr">%s%s</td>'
                     u'<td class="n">%d</td><td class="en">%s</td><td class="n">%d</td></tr>'
                     % (u' class="note"' if v["m"] else u"", v["i"],
                        e(v["fr"]).strip() or u"&nbsp;",
                        (u' <span class="ms">%s</span>' % m) if m else u"",
                        v["sfr"], e(v["en"]).strip() or u"&nbsp;", v["sen"]))
    h = (ICI / "temps_gabarit.html").read_text(encoding="utf-8")
    h = h.replace(u"@LIGNES@", u"\n".join(L))
    for cle, val in (
            (u"@MN@", u"%.1f" % T["moy_note"]), (u"@MU@", u"%.1f" % T["moy_nu"]),
            (u"@N@", u"%d" % T["n"]), (u"@SFR@", u"%d" % T["fr"]),
            (u"@SEN@", u"%d" % T["en"]),
            (u"@PCT@", u"%.0f" % (100.0 * T["en"] / T["fr"])),
            (u"@NOTES@", u"%d" % T["notes"]),
            (u"@PN@", u"%.0f" % (100.0 * T["notes"] / T["n"])),
            (u"@DEB@", u"%.2f" % (T["fr"] / float(PLANS * FENETRE))),
            (u"@DMIN@", u"%.2f" % min(p["debit"] for p in P)),
            (u"@DMAX@", u"%.2f" % mx),
            (u"@PMIN@", u"%d" % min(P, key=lambda p: p["debit"])["n"]),
            (u"@PMAX@", u"%d" % max(P, key=lambda p: p["debit"])["n"])):
        h = h.replace(cle, val)
    reste = re.findall(u"@[A-Z]{2,8}@", h)
    if reste:
        sys.exit("jetons non remplaces dans le gabarit : %s" % u", ".join(reste))
    return h


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    d = mesurer()
    T = d["tot"]
    print(u"%d vers chantes, %d syllabes en français, %d en anglais (%.0f %%)"
          % (T["n"], T["fr"], T["en"], 100.0 * T["en"] / T["fr"]))
    print(u"%d vers notes, %.1f syllabes en moyenne, contre %.1f sans notation : %+.0f %%"
          % (T["notes"], T["moy_note"], T["moy_nu"],
             100.0 * (T["moy_note"] / T["moy_nu"] - 1)))
    q4 = sum(1 for p in d["plans"] if p["nvers"] == 4)
    print(u"%d plans de 4 vers, %d de 3" % (q4, PLANS - q4))
    print(u"debit de %.2f a %.2f syllabes/s"
          % (min(p["debit"] for p in d["plans"]), max(p["debit"] for p in d["plans"])))
    if "--table" in sys.argv[1:]:
        for p in d["plans"]:
            v = next(x for x in d["vers"] if x["plan"] == p["n"])
            print(u"  plan %2d  %3d-%3d s  %d vers  %4.2f syl/s  %s"
                  % (p["n"], p["t0"], p["t1"], p["nvers"], p["debit"], v["fr"][:40]))
        sys.exit(0)
    (ICI / "temps_data.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8", newline="\n")
    h = page(d)
    (ICI / "temps_toxicosqueros.html").write_text(h, encoding="utf-8", newline="\n")
    print(u"\ntemps_data.json et temps_toxicosqueros.html ecrits (%d caracteres)" % len(h))
