# -*- coding: utf-8 -*-
"""Extrait le texte d'un PDF a flux FlateDecode, sans dependance.

Sert a lire les documents que Takiwasi publie lui-meme : sur la question du
financement public, leur propre texte est la source la plus forte possible.
"""
import re
import sys
import zlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CHAINE = re.compile(rb"\((?:\\.|[^()\\])*\)", re.S)


def texte(chemin):
    b = open(chemin, "rb").read()
    morceaux = []
    for m in re.finditer(rb"stream\r?\n", b):
        fin = b.find(b"endstream", m.end())
        if fin < 0:
            continue
        try:
            s = zlib.decompress(b[m.end():fin])
        except Exception:
            continue
        if b"Tj" not in s and b"TJ" not in s:
            continue
        out = []
        for t in CHAINE.finditer(s):
            x = t.group(0)[1:-1]
            x = x.replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")
            out.append(x)
        # Un TJ sans espace entre ses morceaux : on recolle sans separateur,
        # sinon chaque syllabe devient un mot.
        morceaux.append(b"".join(out))
    return len(b), b"\n".join(morceaux).decode("latin-1", "replace")


MOTS = ("financ", "subvention", "DGLDT", "DGLCDT", "lutte contre la drogue",
        "minist", "Affaires", "Coop", "europ", "Union", "ambassade",
        "ONU", "Nations", "don ", "budget")

if __name__ == "__main__":
    n, plein = texte(sys.argv[1])
    print("pdf %d octets, texte %d caracteres" % (n, len(plein)))
    plat = re.sub(r"\s+", " ", plein)
    phrases = re.split(r"(?<=[.!?]) ", plat)
    vus = set()
    for p in phrases:
        if len(p) < 40:
            continue
        if not any(w.lower() in p.lower() for w in MOTS):
            continue
        cle = p[:50]
        if cle in vus:
            continue
        vus.add(cle)
        print("\n  * " + p.strip()[:700])
