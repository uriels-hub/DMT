# -*- coding: utf-8 -*-
"""Extrait le texte d'un PDF, sans dependance.

Sert a lire les documents que les institutions publient elles-memes : sur la
question du financement d'un centre, sur le contenu d'un rapport officiel ou
d'une decision de justice, leur propre texte est la source la plus forte.

DEUX FAMILLES DE PDF, ET IL FAUT LES DEUX.

Les PDF d'editeur et d'administration posent leur texte en chaines litterales,
entre parentheses : il suffit de decompresser le flux et de les lire.

Les PDF imprimes depuis un navigateur — Chrome produit « Skia/PDF » — posent
chaque glyphe en hexadecimal, <009D>, et renvoient a une table ToUnicode qui
dit quel caractere se cache derriere. Sans cette table, l'extraction rend
quatre caracteres sur un article entier, ce qui est arrive. On lit donc
d'abord toutes les tables du document, puis on decode.

    python pdftxt.py document.pdf
    python pdftxt.py document.pdf motcle1 motcle2   # ne sort que les passages

DEUX LIMITES CONSTATEES, a connaitre avant de conclure.

Les tables ToUnicode sont fusionnees en une seule. Quand un document emploie
plusieurs polices dont les numeros de glyphes se recouvrent, quelques
fragments ressortent decales d'un cran dans l'alphabet — « Ulwxdo » pour
« Ritual ». Le corps du texte reste lisible ; un fragment chiffre ainsi
signale une en-tete ou un pied de page, rarement du contenu.

Surtout : une page d'editeur enregistree en PDF depuis un navigateur ne
contient pas l'article. Elle contient le menu, le resume des rubriques, la
liste des references et le bouton d'achat. L'extraction rendra « Abstract »
comme intitule et « Purchase PDF » juste a cote, sans une ligne de donnees.
Verifier la presence de mots du contenu avant de citer quoi que ce soit.
"""
import io
import re
import sys
import zlib

CHAINE = re.compile(rb"\((?:\\.|[^()\\])*\)", re.S)
HEXTJ = re.compile(rb"<([0-9A-Fa-f]+)>\s*Tj")
HEXTJ_ARR = re.compile(rb"\[((?:\s*<[0-9A-Fa-f]+>|\s*-?[\d.]+)+)\s*\]\s*TJ")
HEXDANS = re.compile(rb"<([0-9A-Fa-f]+)>")


def flux(b):
    """Chaque flux decompressable du fichier."""
    for m in re.finditer(rb"stream\r?\n", b):
        fin = b.find(b"endstream", m.end())
        if fin < 0:
            continue
        try:
            yield zlib.decompress(b[m.end():fin])
        except Exception:
            continue


def _uni(h):
    """Une cible ToUnicode : suite d'unites UTF-16BE."""
    try:
        return bytes.fromhex(h.decode("ascii")).decode("utf-16-be", "replace")
    except Exception:
        return u""


def table_unicode(flots):
    """Fusionne les tables ToUnicode du document : glyphe -> caractere."""
    t = {}
    for d in flots:
        if b"beginbfchar" not in d and b"beginbfrange" not in d:
            continue
        for bloc in re.findall(rb"beginbfchar(.*?)endbfchar", d, re.S):
            for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>",
                                       bloc):
                t.setdefault(int(src, 16), _uni(dst))
        for bloc in re.findall(rb"beginbfrange(.*?)endbfrange", d, re.S):
            # <lo> <hi> <dst> : une plage contigue
            for lo, hi, dst in re.findall(
                    rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>",
                    bloc):
                a, z, base = int(lo, 16), int(hi, 16), int(dst, 16)
                # Une plage reelle compte quelques centaines de glyphes. Au-dela,
                # c'est une table pathologique ou un faux positif : la deplier
                # ferait boucler l'outil sur un gros document, ce qui est arrive.
                if z - a > 2048:
                    continue
                for i in range(a, z + 1):
                    t.setdefault(i, chr(base + i - a))
            # <lo> <hi> [<d1> <d2> ...] : une cible par code
            for lo, _hi, liste in re.findall(
                    rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*\[(.*?)\]",
                    bloc, re.S):
                a = int(lo, 16)
                for i, dst in enumerate(HEXDANS.findall(liste)):
                    t.setdefault(a + i, _uni(dst))
    return t


def _glyphes(h, t):
    """Une chaine hexadecimale, lue par unites de deux octets."""
    s = h.decode("ascii")
    return u"".join(t.get(int(s[i:i + 4], 16), u"")
                    for i in range(0, len(s) - 3, 4))


def texte(chemin):
    """Le texte du document, et la taille de la table si elle a servi.

    On tente d'abord les chaines litterales, qui couvrent les PDF d'editeur
    et d'administration et ne coutent rien. On ne construit la table
    ToUnicode que si cette premiere passe ne rend presque rien : la batir
    suppose de parcourir tous les flux du document, ce qui fait boucler
    l'outil plusieurs minutes sur un rapport de mille pages.
    """
    b = io.open(chemin, "rb").read()
    flots = [d for d in flux(b) if b"Tj" in d or b"TJ" in d]

    litteral = []
    for d in flots:
        morceau = []
        for m in CHAINE.finditer(d):
            x = m.group(0)[1:-1]
            x = x.replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")
            morceau.append(x)
        if morceau:
            litteral.append(b"".join(morceau).decode("latin-1", "replace"))
    plein = u"\n".join(litteral)
    if len(plein.strip()) > 200:
        return len(b), plein, 0

    # Deuxieme passe : glyphes hexadecimaux des PDF de navigateur.
    t = table_unicode(flux(b))
    hexa = []
    for d in flots:
        hx = [_glyphes(m.group(1), t) for m in HEXTJ.finditer(d)]
        for m in HEXTJ_ARR.finditer(d):
            hx.append(u"".join(_glyphes(x, t)
                               for x in HEXDANS.findall(m.group(1))))
        if hx:
            hexa.append(u"".join(hx))
    return len(b), u"\n".join(litteral + hexa), len(t)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    n, plein, nt = texte(sys.argv[1])
    plat = re.sub(r"\s+", " ", plein)
    print(u"pdf %d octets, texte %d caracteres, table ToUnicode de %d glyphes"
          % (n, len(plein), nt))
    mots = sys.argv[2:]
    if not mots:
        print(plat)
    else:
        vus = set()
        for p in re.split(r"(?<=[.!?]) ", plat):
            if len(p) < 30 or not any(m.lower() in p.lower() for m in mots):
                continue
            if p[:50] in vus:
                continue
            vus.add(p[:50])
            print(u"\n  * " + p.strip()[:700])
