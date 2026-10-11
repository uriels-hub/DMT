# -*- coding: utf-8 -*-
"""Croise les elements valides de l'extrait avec ce que la page contient.

La question posee est simple et merite une reponse mesuree, pas une
impression : ce qui a ete valide dans le rapport v2 se trouve-t-il, ou non,
sur la page publique ?

Trois sorties : present, absent, et « theme non couvert » pour ce qui n'a pas
de PMID parce que la page n'en traite pas du tout.
"""
import io
import json
import pathlib
import re
import sys

ICI = pathlib.Path(__file__).resolve().parent.parent

# Chaque element valide de la note, avec son identifiant quand il en a un.
VALIDES = [
    ("12925718", u"Dunkley, criteres de Hunter"),
    ("2035713",  u"Sternbach, description princeps"),
    ("38926083", u"Chiew, prise en charge"),
    ("22563571", u"Perry, syndrome serotoninergique contre syndrome malin"),
    ("34251464", u"Malcolm & Thomas, toxicite des psychedeliques"),
    ("25713771", u"Szmulewicz 2015, virage maniaque apres ayahuasca"),
    ("37810598", u"Halim 2023, episode maniaque apres psilocybine"),
    ("41329646", u"Myran, cohorte de l'Ontario"),
    ("20126400", u"Ray 2010, receptorome : source primaire des Ki"),
    ("27216487", u"Rickli 2016, profils de liaison des tryptamines"),
    ("39564729", u"Yildirim 2024, effets psychiatriques indesirables"),
    ("39230883", u"Hinkle 2024, evenements indesirables"),
    ("20716786", u"Elangbam, valvulopathies medicamenteuses"),
    ("24817577", u"Szymanski, benfluorex et valves"),
    ("28129538", u"Wacker, structure LSD / 5-HT2B"),
    ("26634934", u"Lavita, beta-carbolines et tremblement essentiel"),
    ("20512126", u"Murray, activite constitutive des 5-HT2C"),
    ("28856708", u"El Oussini, degenerescence serotoninergique et spasticite"),
    ("30625007", u"Lucas-Osma, 5-HT1D et reflexe myotatique"),
    ("21075681", u"Seo, retard au relachement musculaire"),
]

# Ce qui n'a pas de PMID : on cherche par mot-cle dans tout le contenu.
THEMES = [
    (u"Cassation, etat anterieur",        (u"21-12.657", u"21-12657", u"predisposition pathologique")),
    (u"Conseil d'Etat 2024",              (u"487157",)),
    (u"MIVILUDES 2005",                   (u"MIVILUDES",)),
    (u"Deontologie, devoir d'information", (u"R4127-35", u"R4127-32", u"perte de chance")),
    (u"Troubles neurologiques fonctionnels", (u"fonctionnel", u"functional neurolog", u"FND",
                                              u"conversion disorder")),
    (u"Examens neuro-ophtalmologiques",   (u"Farnsworth", u"tritanop", u"OCT", u"GCIPL",
                                           u"potentiels evoques", u"P100", u"electroretinog")),
    (u"Xanthopsie / vision des couleurs", (u"xanthops", u"chromatique", u"color vision",
                                           u"tritan")),
    (u"Echocardiographie",                (u"echocardiograph", u"valvulopath", u"valve",
                                           u"5-HT2B")),
    (u"Depersonnalisation",               (u"depersonaliz", u"depersonnalis", u"derealiz")),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    au = json.loads((ICI / "page_autres.json").read_text(encoding="utf-8"))

    ou = {}
    for g in gr:
        for r in g["refs"]:
            ou[r["pmid"]] = (g["cat"], g["titre"])

    # Tout le texte de la page, pour la recherche par mot-cle.
    plein = json.dumps(gr, ensure_ascii=False) + json.dumps(au, ensure_ascii=False)
    plein_bas = plein.lower()

    print(u"=" * 76)
    print(u"ELEMENTS VALIDES PORTANT UN PMID")
    print(u"=" * 76)
    absents = []
    for pmid, lib in VALIDES:
        if pmid in ou:
            cat, titre = ou[pmid]
            print(u"  [present] %-9s %-52s" % (pmid, lib[:52]))
            print(u"             -> %s / %s" % (cat, titre[:46]))
        else:
            absents.append((pmid, lib))
    if absents:
        print(u"\n  ABSENTS DE LA PAGE :")
        for pmid, lib in absents:
            print(u"    %-9s %s" % (pmid, lib))

    print(u"\n" + u"=" * 76)
    print(u"ELEMENTS SANS PMID : couverture thematique")
    print(u"=" * 76)
    for nom, mots in THEMES:
        trouves = [m for m in mots if m.lower() in plein_bas]
        etat = u"couvert" if trouves else u"ABSENT "
        print(u"  [%s] %-38s %s" % (etat, nom,
              (u"mots trouves : " + u", ".join(trouves[:3])) if trouves else u""))

    print(u"\n" + u"=" * 76)
    print(u"BILAN")
    print(u"=" * 76)
    n = len(VALIDES)
    print(u"  %d des %d references validees sont sur la page (%d absentes)."
          % (n - len(absents), n, len(absents)))
    manque = [nom for nom, mots in THEMES
              if not any(m.lower() in plein_bas for m in mots)]
    print(u"  %d des %d themes sans PMID ne sont pas couverts%s"
          % (len(manque), len(THEMES), (u" : " + u", ".join(manque)) if manque else u"."))


if __name__ == "__main__":
    main()
