# -*- coding: utf-8 -*-
"""Pose sur la page le profil d'affinite reel de la DMT.

Les chiffres ne sont pas recopies : ils sont lus dans le tableau S2 de
Ray 2010, telecharge depuis PLoS ONE, qui porte les donnees brutes du
programme de criblage NIMH-PDSP. C'est la source primaire.

Raison d'etre : un tableau circule, repris d'une revue secondaire, qui donne
pour la DMT des valeurs introuvables dans cette source et parfois
contradictoires avec elle. Le tableau ci-dessous le remplace.
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

# Libelles lisibles pour les sites retenus au tableau.
NOMS = {
    "5ht7": u"5-HT7", "5ht1d": u"5-HT1D", "5ht2b": u"5-HT2B",
    "Alpha2B": u"α2B", "Alpha2C": u"α2C", "D1": u"D1",
    "5ht2c": u"5-HT2C", "5ht1e": u"5-HT1E", "5ht6": u"5-HT6",
    "5ht5a": u"5-HT5A", "5ht2a": u"5-HT2A", "SERT": u"SERT",
    "Sigma1": u"σ1", "5ht1a": u"5-HT1A", "5ht1b": u"5-HT1B",
}
# Ce que le document a corriger annonce, pour la colonne de comparaison.
DOCX = {"5ht1d": "39", "5ht2a": "127", "5ht1b": "129",
        "5ht1a": "183", "5ht2b": "184"}

AJOUT = (
    u"\n\n<strong>Le profil d\u2019affinité réel, et pourquoi il faut le "
    u"poser ici.</strong> Un tableau circule, repris de revues secondaires, qui "
    u"attribue à la DMT une affinité forte pour le 5-HT2A — de l\u2019ordre de "
    u"127\u202fnM — et des affinités mesurables pour les 5-HT1A et 5-HT1B. Les "
    u"données brutes du programme de criblage NIMH-PDSP, publiées en annexe de "
    u"Ray\u202f2010, disent autre chose. Le site le plus affin est le "
    u"<em>5-HT7</em>, que ce tableau-là ne mentionne pas ; le 5-HT2A y est à "
    u"2323\u202fnM, soit une affinité faible ; et les 5-HT1A et 5-HT1B y sont "
    u"au-delà de 10\u202f000\u202fnM, c\u2019est-à-dire sans affinité mesurable. "
    u"Rickli et ses collègues, dans un laboratoire indépendant, confirment le "
    u"sens de la correction\u202f: l\u2019affinité de la DMT pour le 5-HT2A est "
    u"<em>inférieure</em> à celle du LSD.\n\n"
    u"Cela ne retire rien au rôle du 5-HT2A, qui reste établi par voie "
    u"fonctionnelle — la kétansérine supprime l\u2019effet. Une affinité de "
    u"liaison modeste et une activation fonctionnelle réelle ne sont pas "
    u"contradictoires. Mais un tableau de chiffres faux, lui, se vérifie en dix "
    u"minutes, et emporte tout le reste avec lui.\n\n"
    u"Un point mérite d\u2019être relevé\u202f: dans ces données, le "
    u"<strong>5-HT2B est le troisième site le plus affin de la molécule</strong> "
    u"— c\u2019est-à-dire le récepteur dont l\u2019activation fibrose les valves "
    u"cardiaques, traité au groupe sur la consommation répétée."
)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    s = xlrd.open_workbook(str(XLS)).sheet_by_index(0)
    ent = [str(s.cell_value(0, c)).strip() for c in range(s.ncols)]
    ligne = None
    for r in range(s.nrows):
        if str(s.cell_value(r, 0)).strip().upper() == "DMT":
            ligne = [str(s.cell_value(r, c)).strip() for c in range(s.ncols)]
            break
    if ligne is None:
        sys.exit("ligne DMT introuvable dans le tableau S2")

    brut = dict(zip(ent, ligne))
    mesures = []
    for cle, val in brut.items():
        if cle not in NOMS:
            continue
        try:
            mesures.append((float(val), cle))
        except ValueError:
            mesures.append((float("inf"), cle))
    mesures.sort()

    lignes = []
    for v, cle in mesures:
        affiche = u"%.1f" % v if v != float("inf") else u"> 10 000"
        cmp = DOCX.get(cle, u"—")
        lignes.append({"cells": [NOMS[cle], affiche, cmp],
                       "fort": cle in ("5ht7", "5ht1d", "5ht2b")})

    tab = {
        "titre": u"Affinité de la DMT, Ki en nanomoles par litre",
        "colonnes": [u"Site", u"Ray 2010 (NIMH-PDSP)", u"Tableau en circulation"],
        "lignes": lignes,
        "source": (u"Données brutes du tableau S2 de Ray, PLoS ONE 2010 "
                   u"(PMID 20126400), criblage NIMH-PDSP. Un Ki bas signifie une "
                   u"affinité forte. Les trois sites les plus affins sont "
                   u"signalés. La dernière colonne reproduit les valeurs du "
                   u"tableau que cette page corrige."),
    }

    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    n = 0
    for g in gr:
        if g["titre"].startswith(CIBLE):
            g["tableau"] = tab
            if u"profil d\u2019affinité réel" not in g["intro"]:
                g["intro"] += AJOUT
            n += 1
            print(u"tableau posé dans : %s" % g["titre"])
    if not n:
        sys.exit(u"groupe introuvable : %s" % CIBLE)

    with io.open(str(ICI / "page_data.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        f.write(json.dumps(gr, ensure_ascii=False, indent=1) + "\n")

    print()
    print(u"  %-10s %14s %14s" % (u"site", u"Ray 2010", u"tableau docx"))
    for l in lignes:
        a, b, c = l["cells"]
        print(u"  %-10s %14s %14s%s" % (a, b, c, u"   <<" if l["fort"] else u""))


if __name__ == "__main__":
    main()
