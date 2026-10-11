# -*- coding: utf-8 -*-
"""Pose sous le tableau ce que ses chiffres etablissent.

Un tableau sans lecture n'est qu'un ornement, et un lecteur presse en tirera
la conclusion qui l'arrange. Les sept points ci-dessous sont ceux que les deux
jeux de donnees soutiennent ensemble, y compris quand ils limitent la portee
du tableau.
"""
# APPLIQUE UNE FOIS. Le resultat de ce script est deja dans
# page_data.json : le relancer n’apporterait rien, et il refuserait
# de s’executer puisque le groupe existe deja. Il est conserve parce
# qu’une page qui affirme que rien n’est ecrit a la main doit
# pouvoir montrer par quoi sa donnee est passee.
import io
import json
import pathlib
import sys

ICI = pathlib.Path(__file__).resolve().parent.parent
CIBLE = u"La DMT est-elle un dissociatif"

LECTURE = [
    u"<strong>Les deux jeux s\u2019accordent sur six sites de dix</strong>, et sur "
    u"trois d\u2019entre eux à 10\u202f% près — 5-HT2C, 5-HT6, 5-HT1E. Ce ne sont "
    u"pas deux mesures incompatibles\u202f: ce sont deux laboratoires qui "
    u"retrouvent la même molécule, et qui divergent sur une minorité de sites.",

    u"<strong>Le désaccord est orienté, pas dispersé.</strong> Sur les trois "
    u"sites où l\u2019écart est majeur — 5-HT2A, 5-HT1B, 5-HT1A — il va toujours "
    u"dans le même sens. Une erreur de mesure serait aléatoire\u202f; une "
    u"différence de méthode est systématique. C\u2019est une différence de "
    u"méthode, et le radioligand employé suffit souvent à l\u2019expliquer.",

    u"<strong>Un argument extérieur départage sur le 5-HT2A.</strong> Dans un "
    u"même jeu, la DMT est à 2323\u202fnM, la psilocine à 340 et le LSD à 11,3. "
    u"Cet ordre reproduit celui des doses actives chez l\u2019homme — quelques "
    u"dizaines de milligrammes, une vingtaine de milligrammes, une centaine de "
    u"microgrammes. Rickli et ses collègues l\u2019écrivent explicitement\u202f: "
    u"l\u2019affinité de liaison des tryptamines corrèle avec les doses "
    u"psychoactives rapportées.",

    u"<strong>La DMT n\u2019est un ligand puissant de rien.</strong> Son meilleur "
    u"Ki vaut 87,5\u202fnM, soit vingt-deux fois moins que le meilleur du LSD. "
    u"Elle touche beaucoup de cibles, moyennement, aucune fortement. Ce "
    u"n\u2019est pas une remarque de nomenclature\u202f: un ligand faible et peu "
    u"sélectif exige des concentrations élevées pour agir, et à ces "
    u"concentrations il engage <em>plusieurs cibles à la fois</em>. "
    u"L\u2019effet n\u2019est réductible à aucun récepteur unique.",

    u"<strong>Le paradoxe du 5-HT2A se résout, et il coupe des deux "
    u"côtés.</strong> Les deux jeux placent ce récepteur hors du trio de tête, "
    u"alors que l\u2019effet psychédélique passe bien par lui puisque la "
    u"kétansérine le supprime. L\u2019explication est dans le tableau même\u202f: "
    u"la psilocine y est à 340\u202fnM sur ce récepteur et nul ne conteste "
    u"qu\u2019elle agisse. Une affinité de liaison modeste et une activation "
    u"fonctionnelle réelle ne sont pas contradictoires — et l\u2019on "
    u"n\u2019argumente donc la puissance ni dans un sens ni dans l\u2019autre "
    u"depuis un tableau de liaison.",

    u"<strong>Le 5-HT7 est le site que personne n\u2019exploite.</strong> "
    u"Premier dans un jeu, sixième dans l\u2019autre, et Ray relève que la DMT "
    u"est la seule des trente-cinq molécules de sa série dont la meilleure "
    u"interaction s\u2019y situe. Ce récepteur gouverne le rythme circadien, "
    u"l\u2019humeur et la formation des épines dendritiques. Or l\u2019harmine, "
    u"dans le même breuvage, allonge la période de l\u2019horloge circadienne "
    u"par une tout autre voie. Les deux alcaloïdes convergent sur "
    u"l\u2019horloge.",

    u"<strong>Le sigma-1 est faible dans les deux jeux</strong>\u202f: "
    u"5209\u202fnM d\u2019un côté, un Kd d\u2019environ 15\u202fµM de "
    u"l\u2019autre — soit soixante fois moins affine que le meilleur site de la "
    u"molécule. Occuper la moitié de ces récepteurs suppose donc une "
    u"concentration libre de l\u2019ordre du micromolaire. Savoir si les doses "
    u"réelles l\u2019atteignent est une question de concentrations mesurées, pas "
    u"d\u2019affinité, et le tableau ne la tranche pas.",
]

AVERTISSEMENT = (
    u"Enfin, ce qu\u2019aucune de ces lignes ne permet\u202f: il s\u2019agit de "
    u"liaison <em>in vitro</em>. Pas de concentration, pas de durée, pas de "
    u"personne. Un tableau d\u2019affinité dit ce qu\u2019une molécule peut "
    u"toucher. Il ne dit jamais ce qu\u2019elle a fait à quelqu\u2019un."
)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    n = 0
    for g in gr:
        if not g["titre"].startswith(CIBLE):
            continue
        if not g.get("tableau"):
            sys.exit(u"le groupe ne porte pas de tableau")
        g["tableau"]["lecture"] = LECTURE
        if u"aucune de ces lignes ne permet" not in g["intro"]:
            g["intro"] += u"\n\n" + AVERTISSEMENT
        n += 1
    if not n:
        sys.exit(u"groupe introuvable")
    with io.open(str(ICI / "page_data.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        f.write(json.dumps(gr, ensure_ascii=False, indent=1) + "\n")
    print(u"%d points de lecture posés sous le tableau." % len(LECTURE))
    for i, x in enumerate(LECTURE, 1):
        plat = x.replace(u"<strong>", u"").replace(u"</strong>", u"")
        plat = plat.replace(u"<em>", u"").replace(u"</em>", u"")
        print(u"  %d. %s" % (i, plat[:88]))


if __name__ == "__main__":
    main()
