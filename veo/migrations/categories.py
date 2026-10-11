# -*- coding: utf-8 -*-
"""Range les 26 groupes en 5 categories, et regroupe les libelles hors PubMed.

Pourquoi : les groupes se sont ajoutes un par un au fil du travail. L'ordre de
la page est donc chronologique, pas thematique, et un lecteur qui cherche la
pharmacologie la trouve en trois endroits. Les categories ci-dessous sont
ecrites a la main une fois ; l'appartenance est ensuite portee par les donnees.

Le script refuse de s'executer si un groupe n'est pas classe ou si un titre
cite ici n'existe pas : c'est ce qui evite qu'un ajout futur disparaisse de la
page sans que personne ne le voie.
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

# Ordre des categories = ordre de lecture de la page. Il va du mecanisme vers
# le discours : ce que la molecule fait, ce que le corps subit, ce qu'on peut
# mesurer, ce que les chiffres valent, ce que le groupe en dit.
CATS = [
    (u"Pharmacologie et mécanismes",
     u"Ce que les molécules font, et par quels récepteurs.",
     [u"Pharmacologie et doses répétées",
      u"Dépendance, tolérance, pharmacologie",
      u"Accoutumance : le corps s'habitue, pas l'expérience",
      u"La consommation répétée : ce qui se dérègle, et l’inquiétude valvulaire",
      u"L'axe dopaminergique des bêta-carbolines",
      u"Sérotonine et tonus musculaire : rigidité, relâchement, tremblement",
      u"La DMT est-elle un dissociatif ?",
      u"Les dissociatifs : kétamine, dextrométhorphane, protoxyde d'azote"]),

    (u"Clinique et séquelles",
     u"Ce qui est rapporté chez des personnes, du cas grave à la séquelle durable.",
     [u"Séquelles perceptives persistantes",
      u"Toxicité, événements indésirables, décès",
      u"Psychose et suicidalité",
      u"Cas graves rapportés",
      u"Mineurs, grossesse, adolescence",
      u"L'iboga, et pourquoi l'autopsie ne trouve rien"]),

    (u"Ce que les examens trouvent",
     u"La preuve matérielle : ce qu'un prélèvement montre, ce qu'il manque, "
     u"et ce qui n'est jamais cherché.",
     [u"Ce que les examens cherchent, et ne cherchent pas",
      u"Ce que le corps garde, et pour combien de temps",
      u"Déclaration et attribution aux urgences"]),

    (u"Épidémiologie et valeur de la preuve",
     u"Ce que les grands nombres établissent, et ce qui limite les études "
     u"elles-mêmes.",
     [u"La cohorte de l'Ontario",
      u"Qui mène les études, et ce que l'insu ne couvre pas"]),

    (u"Emprise, discours et dérive",
     u"Comment un dommage se fait reformuler en progrès, et qui a intérêt à "
     u"cette reformulation.",
     [u"Emprise, abus, consentement",
      u"Le contexte du rituel",
      u"Le mot « enthéogène » et l'expérience mystique",
      u"Réinterprétation du symptôme, réattribution de la cause",
      u"Le groupe comme censeur",
      u"Le mythe du révélateur",
      u"Takiwasi : ce qu’écrit la MIVILUDES, et d’où vient l’argent"]),
]

# Les libelles hors PubMed s'etaient fragmentes : douze etiquettes pour
# vingt-huit sources, dont six a entree unique. Regroupement.
FUSION = {
    u"Mineurs : le droit français": u"Droit français",
    u"Juridiction française": u"Droit français",
    u"Rapports publics français": u"Rapports publics et institutions",
    u"Rapport officiel français": u"Rapports publics et institutions",
    u"Association reconnue d’utilité publique": u"Rapports publics et institutions",
    u"Médecine légale et toxicologie française": u"Médecine légale et toxicologie",
    u"Nosographie": u"Nosographie internationale",
    u"Histoire du vocabulaire": u"Travaux universitaires et sources primaires",
    u"Thèse de référence": u"Travaux universitaires et sources primaires",
    u"La source le dit elle-même": u"Travaux universitaires et sources primaires",
}
ORDRE_AUTRES = [
    u"Droit français",
    u"Jurisprudence étrangère",
    u"Nosographie internationale",
    u"Rapports publics et institutions",
    u"Médecine légale et toxicologie",
    u"Travaux universitaires et sources primaires",
    u"Le secteur des retraites",
]


def cle(t):
    """Titre reduit a ce qui l'identifie.

    Les titres portent la typographie francaise : espace insecable avant les
    deux-points, apostrophe courbe ou droite selon le jour. Comparer les
    octets fait echouer le classement sur un caractere invisible. On compare
    donc le titre normalise, en gardant l'original dans la donnee.
    """
    for a, b in ((u" ", u" "), (u" ", u" "), (u"’", u"'")):
        t = t.replace(a, b)
    return u" ".join(t.split()).lower()


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    au = json.loads((ICI / "page_autres.json").read_text(encoding="utf-8"))

    # Deux controles symetriques : aucun groupe orphelin, aucun titre fantome.
    titres = set(cle(g["titre"]) for g in gr)
    classes = [cle(t) for _, _, lst in CATS for t in lst]
    brut = dict((cle(t), t) for _, _, lst in CATS for t in lst)
    fantomes = [brut[t] for t in classes if t not in titres]
    orphelins = [g["titre"] for g in gr if cle(g["titre"]) not in classes]
    if fantomes:
        print(u"TITRES CITES QUI N'EXISTENT PAS :")
        for t in fantomes:
            print(u"    %s" % t)
    if orphelins:
        print(u"GROUPES NON CLASSES :")
        for t in orphelins:
            print(u"    %s" % t)
    if len(classes) != len(set(classes)):
        sys.exit(u"un titre est classe deux fois")
    if fantomes or orphelins:
        sys.exit(u"classement incomplet, rien n'a ete ecrit")

    # On ecrit la categorie dans la donnee, et on reordonne la liste.
    rang = {}
    for i, (nom, _, lst) in enumerate(CATS):
        for j, t in enumerate(lst):
            rang[cle(t)] = (i, j)
    for g in gr:
        i, _ = rang[cle(g["titre"])]
        g["cat"] = CATS[i][0]
    gr.sort(key=lambda g: rang[cle(g["titre"])])

    print(u"26 groupes rangés en %d catégories :\n" % len(CATS))
    for nom, sous, lst in CATS:
        n = sum(len(g["refs"]) for g in gr if g["cat"] == nom)
        print(u"  %-38s %2d groupes  %3d notices" % (nom, len(lst), n))

    # Hors PubMed : fusion des libelles, puis tri selon ORDRE_AUTRES.
    for a in au:
        a["grp"] = FUSION.get(a["grp"], a["grp"])
    restants = [a["grp"] for a in au if a["grp"] not in ORDRE_AUTRES]
    if restants:
        sys.exit(u"libelle hors PubMed non prevu : %s" % ", ".join(sorted(set(restants))))
    au.sort(key=lambda a: ORDRE_AUTRES.index(a["grp"]))

    print(u"\nhors PubMed : 12 libellés ramenés à %d\n" % len(ORDRE_AUTRES))
    for nom in ORDRE_AUTRES:
        print(u"  %-44s %d" % (nom, sum(1 for a in au if a["grp"] == nom)))

    for nom, obj in (("page_data.json", gr), ("page_autres.json", au)):
        with io.open(str(ICI / nom), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")
    print(u"\npage_data.json et page_autres.json réécrits.")


if __name__ == "__main__":
    main()
