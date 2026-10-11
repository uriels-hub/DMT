# -*- coding: utf-8 -*-
"""Extrait le texte d'un .docx, paragraphe par paragraphe, sans dependance.

Garde la structure : un titre de niveau n devient une ligne prefixee, un
element de liste devient une puce. Sert a relire un document long sans le
paraphraser de memoire.
"""
import io
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def paras(chemin):
    import xml.etree.ElementTree as ET
    z = zipfile.ZipFile(chemin)
    noms = [n for n in z.namelist() if n.startswith("word/") and n.endswith(".xml")]
    xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    out = []
    for p in root.iter(W + "p"):
        # Le style du paragraphe dit s'il s'agit d'un titre ou d'une liste.
        style, liste = "", False
        pr = p.find(W + "pPr")
        if pr is not None:
            s = pr.find(W + "pStyle")
            if s is not None:
                style = s.get(W + "val") or ""
            liste = pr.find(W + "numPr") is not None
        txt = "".join(t.text or "" for t in p.iter(W + "t"))
        txt = re.sub(r"\s+", " ", txt).strip()
        if not txt:
            continue
        m = re.match(r"(?i)heading(\d)", style)
        if m:
            out.append(("h%s" % m.group(1), txt))
        elif liste:
            out.append(("li", txt))
        else:
            out.append(("p", txt))
    return out, z, noms


if __name__ == "__main__":
    ps, z, noms = paras(sys.argv[1])
    medias = [n for n in z.namelist() if n.startswith("word/media/")]
    mots = sum(len(t.split()) for _, t in ps)
    print(u"%d paragraphes, %d mots, %d images incorporees"
          % (len(ps), mots, len(medias)))
    print(u"parties xml : %s" % ", ".join(n[5:] for n in sorted(noms))[:200])
    print(u"=" * 78)
    for k, t in ps:
        if k.startswith("h"):
            n = int(k[1])
            print(u"\n%s %s" % ("#" * n, t))
        elif k == "li":
            print(u"  - %s" % t)
        else:
            print(t)
