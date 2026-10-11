# -*- coding: utf-8 -*-
"""Audit chiffre d'un rapport : registre rhetorique et qualite des sources.

Deux mesures, et une seule raison de les faire : un expert judiciaire ne lit
pas un rapport comme un lecteur bienveillant. Il cherche l'endroit ou l'auteur
cesse d'evaluer pour plaider, et il verifie la bibliographie. Autant compter
avant lui.
"""
import io
import re
import sys
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Les superlatifs d'un rapport d'expertise. Chacun est une prise pour la
# partie adverse : il signale que l'auteur argumente au lieu de constater.
EXCES = [
    u"irréfutable", u"indiscutable", u"incontestable", u"accablant",
    u"magistralement", u"foudroyant", u"inextricable", u"univoque",
    u"indéniable", u"absolue", u"absolu", u"exhaustive", u"exhaustif",
    u"tempête", u"catastrophe", u"redoutable", u"spectaculaire",
    u"prouve de manière", u"démontre de façon", u"sans équivoque",
    u"véritable", u"littéralement", u"massif", u"massive", u"massivement",
    u"brutalement", u"délétère", u"vital", u"vitale", u"élégance",
    u"prouesse", u"fascinant", u"effrayant", u"angoissant", u"gravissime",
]

# Un domaine qui n'est pas de la litterature a comite de lecture.
PAS_PAIRS = {
    "wikipedia.org": u"encyclopédie collaborative",
    "researchgate.net": u"dépôt d'auteurs, pas une revue",
    "health.clevelandclinic.org": u"blog d'un hôpital",
    "adf.org.au": u"site de prévention associatif",
    "socialsci.libretexts.org": u"manuel pédagogique en ligne",
    "thesupportivecare.com": u"blog commercial",
    "cipra.cl": u"copie de livre hébergée",
    "terapiacognitiva.eu": u"copie de questionnaire hébergée",
    "ndl.ethernet.edu.et": u"copie d'ouvrage hébergée",
    "pepite-depot.univ-lille.fr": u"thèse d'exercice, non indexée",
}
PAIRS = ("pmc.ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov", "doi.org",
         "psychiatryonline.org", "mdpi.com", "cairn.info", "stm.cairn.info",
         "shs.cairn.info", "nature.com", "sciencedirect.com", "springer.com")


def main(chemin):
    t = io.open(chemin, encoding="utf-8").read()
    corps, _, biblio = t.partition(u"Sources des citations")

    print(u"=" * 74)
    print(u"REGISTRE : superlatifs et intensificateurs dans le corps du rapport")
    print(u"=" * 74)
    total, lignes = 0, []
    for m in EXCES:
        n = len(re.findall(r"(?i)" + re.escape(m), corps))
        if n:
            total += n
            lignes.append((n, m))
    for n, m in sorted(lignes, reverse=True):
        print(u"  %3d  %s" % (n, m))
    mots = len(corps.split())
    print(u"\n  %d occurrences pour %d mots, soit une tous les %d mots."
          % (total, mots, mots // max(total, 1)))

    print(u"\n" + u"=" * 74)
    print(u"BIBLIOGRAPHIE : nature reelle des sources citees")
    print(u"=" * 74)
    urls = re.findall(r"https?://[^\s]+", biblio)
    dom = {}
    for u in urls:
        d = (urlparse(u).netloc or "").lower().lstrip("www.")
        dom[d] = dom.get(d, 0) + 1
    hors, dedans, autres = [], [], []
    for d, n in sorted(dom.items(), key=lambda x: -x[1]):
        if d in PAS_PAIRS:
            hors.append((n, d, PAS_PAIRS[d]))
        elif any(p in d for p in PAIRS):
            dedans.append((n, d))
        else:
            autres.append((n, d))
    print(u"\n  %d liens, %d domaines." % (len(urls), len(dom)))
    print(u"\n  NON relus par des pairs — contredit la section 10 :")
    for n, d, q in hors:
        print(u"    %2d  %-30s %s" % (n, d, q))
    print(u"\n  litterature ou editeurs scientifiques :")
    for n, d in dedans:
        print(u"    %2d  %s" % (n, d))
    if autres:
        print(u"\n  a classer :")
        for n, d in autres:
            print(u"    %2d  %s" % (n, d))
    h = sum(n for n, _, _ in hors)
    print(u"\n  %d liens sur %d (%d %%) ne sont pas de la litterature a "
          u"comite de lecture." % (h, len(urls), round(100.0 * h / len(urls))))

    print(u"\n" + u"=" * 74)
    print(u"RENVOIS INTERNES : numeros d'appel de note incoherents")
    print(u"=" * 74)
    for cle in (u"Gard", u"Szmulewicz", u"Halim"):
        for m in re.finditer(re.escape(cle) + u"[^.\\n]{0,80}", corps):
            x = re.sub(r"\s+", " ", m.group(0))
            print(u"  %s" % x[:92])


if __name__ == "__main__":
    main(sys.argv[1])
