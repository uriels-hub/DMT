# -*- coding: utf-8 -*-
"""Corrige le tableau d'affinite : deux jeux publies, et ils divergent.

Premiere version de ce tableau : j'opposais les donnees brutes du NIMH-PDSP
a un « tableau en circulation », en laissant entendre que ce dernier etait
sans source. C'etait faux, et la correction importe plus que le point
initial.

Le tableau en circulation vient de Cameron & Olson, ACS Chemical Neuroscience
2018, revue de reference du laboratoire Olson a Davis, reprise telle quelle
par une revue ulterieure. Ce sont donc deux jeux de donnees publies qui
divergent, et non une invention contre une source.

Ce qui reste vrai, et qui est le vrai defaut du document d'origine : il a
garde cinq lignes sur treize, et supprime celle du 5-HT7 — site parmi les
plus affins dans les DEUX jeux. Son graphique avait en outre supprime la
barre du 5-HT2B.
"""
# APPLIQUE UNE FOIS. Le resultat de ce script est deja dans
# page_data.json : le relancer n’apporterait rien, et il refuserait
# de s’executer puisque le groupe existe deja. Il est conserve parce
# qu’une page qui affirme que rien n’est ecrit a la main doit
# pouvoir montrer par quoi sa donnee est passee.
#
# NON REJOUABLE EN L’ETAT : ce script lisait un fichier de travail
# transitoire, produit par une recherche verifiee et conserve hors du
# depot. Le chemin ci-dessous ne pointe plus sur rien. Le texte qu’il
# a pose, lui, est dans page_data.json.
import io
import json
import pathlib
import sys

import xlrd

ICI = pathlib.Path(__file__).resolve().parent.parent
XLS = pathlib.Path(
    "fichier de travail transitoire, hors depot"
    r"C--Users-uriel-Documents--12-RUE-ANTOINE-CARLES--LYRICS/"
    r"dec6f719-0e04-49f9-9309-e1ada96e0b4c/scratchpad/ray_S2.xls")
CIBLE = u"La DMT est-elle un dissociatif"

# Tableau 1 de Cameron & Olson 2018, releve sur la page de la revue qui le
# reprend. Ordre d'origine conserve.
CO = [("5ht1d", u"5-HT1D", "39"), ("5ht2a", u"5-HT2A", "127"),
      ("5ht1b", u"5-HT1B", "129"), ("5ht1a", u"5-HT1A", "183"),
      ("5ht2b", u"5-HT2B", "184"), ("5ht7", u"5-HT7", "206"),
      ("5ht2c", u"5-HT2C", "360"), ("5ht6", u"5-HT6", "464"),
      ("5ht1e", u"5-HT1E", "517"), ("5ht5a", u"5-HT5A", "2135")]

ANCIEN_DEBUT = u"\n\n<strong>Le profil d\u2019affinité réel"

AJOUT = (
    u"\n\n<strong>Deux jeux de chiffres publiés, et ils divergent.</strong> Les "
    u"affinités de la DMT circulent sous forme d\u2019un tableau repris de "
    u"Cameron et Olson, <cite>ACS Chemical Neuroscience</cite> 2018. Les données "
    u"brutes du criblage NIMH-PDSP, publiées en annexe de Ray\u202f2010, donnent "
    u"des valeurs différentes. Les deux sont citables, et le tableau ci-dessous "
    u"les met côte à côte plutôt que d\u2019en choisir un.\n\n"
    u"L\u2019accord est bon sur les 5-HT2C, 5-HT6 et 5-HT1E. Il est médiocre sur "
    u"les 5-HT1D, 5-HT2B, 5-HT7 et 5-HT5A. Il est spectaculairement mauvais sur "
    u"trois sites\u202f: le 5-HT2A, à 127\u202fnM pour l\u2019un et "
    u"2323\u202fnM pour l\u2019autre, et les 5-HT1A et 5-HT1B, crédités "
    u"d\u2019affinités franches par l\u2019un et déclarés sans affinité mesurable "
    u"par l\u2019autre. De tels écarts sont attendus entre laboratoires\u202f: le "
    u"radioligand, le récepteur cloné ou natif, l\u2019espèce et surtout, pour un "
    u"agoniste, l\u2019état d\u2019affinité du récepteur étudié changent les "
    u"chiffres. Rickli et ses collègues, dans un troisième laboratoire, "
    u"établissent au moins le sens\u202f: l\u2019affinité de la DMT pour le "
    u"5-HT2A est <em>inférieure</em> à celle du LSD.\n\n"
    u"Rien de tout cela n\u2019affaiblit le rôle du 5-HT2A, qui est établi par "
    u"voie fonctionnelle et non par la liaison — la kétansérine supprime "
    u"l\u2019effet. Dans le jeu du PDSP, la psilocine est à 339\u202fnM sur ce "
    u"même récepteur alors qu\u2019elle est indiscutablement active chez "
    u"l\u2019homme\u202f: une affinité de liaison modeste et une activation "
    u"fonctionnelle réelle ne sont pas contradictoires.\n\n"
    u"<strong>Ce qu\u2019il faut surveiller, en revanche, c\u2019est la "
    u"troncature.</strong> Le tableau de Cameron et Olson compte treize lignes. "
    u"La version qui circule n\u2019en garde que cinq, et laisse de côté le "
    u"5-HT7 — qui figure pourtant parmi les sites les plus affins dans les deux "
    u"jeux, et que Ray désigne comme la meilleure interaction de la molécule. "
    u"Dans les deux jeux également, le <strong>5-HT2B compte parmi les sites les "
    u"plus affins</strong>, et la ligne de Cameron et Olson le dit en toutes "
    u"lettres\u202f: ce récepteur «\u202fmaintient les feuillets valvulaires "
    u"cardiaques\u202f». C\u2019est le sujet du groupe sur la consommation "
    u"répétée."
)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    s = xlrd.open_workbook(str(XLS)).sheet_by_index(0)
    ent = [str(s.cell_value(0, c)).strip() for c in range(s.ncols)]
    dmt = None
    for r in range(s.nrows):
        if str(s.cell_value(r, 0)).strip() == "DMT":
            dmt = dict(zip(ent, [str(s.cell_value(r, c)).strip()
                                 for c in range(s.ncols)]))
    if dmt is None:
        sys.exit("ligne DMT introuvable")

    def tri(cle):
        v = dmt.get(cle, "")
        try:
            return float(v)
        except ValueError:
            return float("inf")

    lignes = []
    for cle, nom, co in sorted(CO, key=lambda x: tri(x[0])):
        v = dmt.get(cle, u"—")
        pdsp = u"> 10 000" if v.startswith(">") else v
        lignes.append({"cells": [nom, pdsp, co],
                       "fort": cle in ("5ht7", "5ht1d", "5ht2b")})

    tab = {
        "titre": u"Affinité de la DMT : deux jeux publiés, Ki en nanomoles par litre",
        "colonnes": [u"Site", u"Ray 2010, NIMH-PDSP", u"Cameron et Olson 2018"],
        "lignes": lignes,
        "source": (u"Colonne 2 : données brutes du tableau S2 de Ray, "
                   u"PLoS ONE 2010 (PMID 20126400). Colonne 3 : tableau 1 de "
                   u"Cameron et Olson, ACS Chemical Neuroscience 2018 "
                   u"(PMID 30036036), dont treize lignes au total. Un Ki bas "
                   u"signifie une affinité forte ; le classement suit la "
                   u"colonne 2. Les trois sites les plus affins y sont signalés."),
    }

    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    fait = 0
    for g in gr:
        if not g["titre"].startswith(CIBLE):
            continue
        g["tableau"] = tab
        i = g["intro"].find(ANCIEN_DEBUT)
        if i >= 0:
            g["intro"] = g["intro"][:i] + AJOUT
            print(u"intro corrigée : l'ancienne version opposait une source à "
                  u"un tableau « en circulation ». Remplacée.")
        elif u"Deux jeux de chiffres publiés" not in g["intro"]:
            g["intro"] += AJOUT
        fait += 1
    if not fait:
        sys.exit(u"groupe introuvable")

    with io.open(str(ICI / "page_data.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        f.write(json.dumps(gr, ensure_ascii=False, indent=1) + "\n")

    print()
    print(u"  %-9s %14s %14s" % (u"site", u"Ray/PDSP", u"Cameron-Olson"))
    for l in lignes:
        a, b, c = l["cells"]
        print(u"  %-9s %14s %14s%s" % (a, b, c, u"   <<" if l["fort"] else u""))


if __name__ == "__main__":
    main()
