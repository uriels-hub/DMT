# -*- coding: utf-8 -*-
"""Ajoute le groupe « Sérotonine et tonus musculaire » à la page publique.

Ce groupe répond à une question clinique : l'action sérotoninergique en
intoxication chronique, et la corrélation hyper-rigidité / relâchement.

Trois niveaux, à ne pas confondre, et la page les sépare :
  établi      l'excès de sérotonine produit rigidité et clonus, c'est un
              critère diagnostique, pas une hypothèse
  établi      la sérotonine commande aussi le relâchement, par d'autres
              récepteurs — donc les deux bouts du tonus
  non établi  aucun travail indexé ne décrit un syndrome chronique
              d'alternance rigidité / relâchement après ayahuasca
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
import urllib.request

ICI = pathlib.Path(__file__).resolve().parent.parent
NCBI = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        "?db=pubmed&retmode=json&id=")

TITRE = u"Sérotonine et tonus musculaire : rigidité, relâchement, tremblement"

INTRO = (
    u"Cette question-là trouve ses sources, contrairement à celle du plancher "
    u"pelvien. L\u2019axe sérotoninergique commande le tonus musculaire, et il le "
    u"commande dans les deux sens.\n\n"
    u"<strong>L\u2019excès donne la rigidité, et ce n\u2019est pas une "
    u"hypothèse.</strong> Les critères de Hunter, référence mondiale pour "
    u"diagnostiquer une toxicité sérotoninergique, retiennent le clonus "
    u"inductible, le clonus oculaire, l\u2019hypertonie et l\u2019hyperréflexie "
    u"comme signes <em>diagnostiques</em>. La rigidité y prédomine aux membres "
    u"inférieurs. Le mécanisme est connu : les récepteurs 5-HT2A et 5-HT2C "
    u"augmentent l\u2019excitabilité du motoneurone spinal, le 5-HT2A agissant "
    u"notamment sur le cotransporteur KCC2. Une revue de 2022 porte précisément "
    u"sur la toxicité sérotoninergique des psychédéliques sérotoninergiques.\n\n"
    u"<strong>Mais la sérotonine commande aussi le relâchement.</strong> Le "
    u"récepteur 5-HT1D inhibe le réflexe myotatique monosynaptique. Bloquer la "
    u"sérotonine <em>retarde</em> le relâchement du muscle lors de la préhension. "
    u"Et l\u2019atonie musculaire du sommeil paradoxal exige précisément le "
    u"retrait de l\u2019influx sérotoninergique sur les motoneurones. Le même "
    u"transmetteur tient donc les deux bouts, par des récepteurs différents : "
    u"c\u2019est ce qui rend une fluctuation du tonus pharmacologiquement "
    u"concevable, au lieu d\u2019absurde.\n\n"
    u"<strong>Le point décisif est ailleurs.</strong> Les récepteurs 5-HT2C ont "
    u"une activité <em>constitutive</em> : ils excitent le motoneurone sans "
    u"sérotonine présente. Après perte de l\u2019influx sérotoninergique "
    u"descendant, cette activité devient le moteur principal des spasmes — c\u2019est "
    u"la démonstration parue dans <em>Nature Medicine</em> en 2010. Et la "
    u"dégénérescence des neurones sérotoninergiques <em>déclenche</em> la "
    u"spasticité. Autrement dit l\u2019excès et la déplétion produisent tous deux "
    u"de la rigidité, par deux routes distinctes. La clinique ferme la boucle : la "
    u"cyprohéptadine, antagoniste 5-HT2, est à la fois l\u2019antidote du syndrome "
    u"sérotoninergique et un traitement de la spasticité.\n\n"
    u"<strong>Enfin, ce qui concerne directement l\u2019ayahuasca.</strong> "
    u"L\u2019harmaline, bêta-carboline présente dans la décoction, est le "
    u"<em>modèle animal de référence du tremblement</em> : elle hypersynchronise "
    u"l\u2019olive inférieure sur les cellules de Purkinje, et c\u2019est avec elle "
    u"qu\u2019on fabrique un tremblement en laboratoire depuis des décennies. Une "
    u"revue parue dans <em>Cerebellum</em> examine le rôle des bêta-carbolines dans "
    u"la pathogenèse du tremblement essentiel humain.\n\n"
    u"<strong>La limite, écrite noir sur blanc.</strong> AUCUN TRAVAIL INDEXÉ NE "
    u"DÉCRIT UN SYNDROME CHRONIQUE D\u2019ALTERNANCE HYPER-RIGIDITÉ / RELÂCHEMENT "
    u"APRÈS AYAHUASCA. Les briques pharmacologiques existent chacune, solidement, "
    u"et elles sont ci-dessous. Le syndrome comme tel n\u2019est pas dans la "
    u"littérature. Une hypothèse clinique qui ne trouve pas sa source ne doit pas "
    u"être déguisée en source."
)

PMIDS = [
    # L'exces : la rigidite comme critere diagnostique
    "12925718",   # Dunkley, criteres de Hunter : clonus et hypertonie, diagnostiques
    "2035713",    # Sternbach, la description princeps du syndrome
    "38926083",   # Chiew, prise en charge de la toxicite serotoninergique
    "22563571",   # Perry, syndrome serotoninergique contre syndrome malin des neuroleptiques
    "34251464",   # Malcolm, toxicite serotoninergique des psychedeliques serotoninergiques
    # Le mecanisme au motoneurone
    "26836802",   # Perrier, modulation de l'activite du motoneurone par la serotonine
    "23248270",   # Bos, PNAS : le 5-HT2A regule le cotransporteur KCC2
    # L'autre sens : le relachement
    "30625007",   # Lucas-Osma, le 5-HT1D inhibe le reflexe myotatique monosynaptique
    "21075681",   # Seo, un antagoniste serotoninergique retarde le relachement du muscle
    "28396432",   # Hasegawa, PNAS : neurones serotoninergiques du raphe dorsal et atonie
    # L'activite constitutive, et la rigidite par deplation
    "20512126",   # Murray, Nature Medicine : activite constitutive des 5-HT2C
    "28856708",   # El Oussini, la degenerescence des neurones serotoninergiques donne la spasticite
    "23221402",   # D'Amico, recepteurs 5-HT2 et alpha1 constitutivement actifs
    "31958408",   # De Deurwaerdere, analyse factuelle de l'activite constitutive
    "12736874",   # Meythaler, la cyproheptadine contre la spasticite du sevrage en baclofene
    # Les beta-carbolines et le tremblement
    "26634934",   # Lavita, Cerebellum : les beta-carbolines dans le tremblement essentiel
    "26660708",   # Handforth, relier le tremblement essentiel au cervelet
    "28966877",   # Louis, l'hypothese olivaire du tremblement essentiel
    "17366267",   # Miwa, modeles rongeurs du tremblement
    "33359647",   # Ayipo, pharmacologie des alcaloides beta-carbolines
    # La charge serotoninergique chronique et ses effets moteurs
    "29708207",   # Garrett, bruxisme associe aux ISRS, revue systematique
    "25195948",   # Falisi, psychotropes et bruxisme
]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    if any(g["titre"] == TITRE for g in gr):
        sys.exit(u"groupe déjà présent")

    deja = set(r["pmid"] for g in gr for r in g["refs"])
    ou = dict((r["pmid"], g["titre"]) for g in gr for r in g["refs"])
    neufs = [p for p in PMIDS if p not in deja]
    for p in PMIDS:
        if p in deja:
            print(u"  déjà sur la page, retiré : %s  [%s]" % (p, ou[p][:44]))

    with urllib.request.urlopen(NCBI + ",".join(neufs), timeout=120) as r:
        res = json.loads(r.read().decode("utf-8"))["result"]

    DOUTEUX = ("correction to", "erratum", "corrigendum", "retraction",
               "author correction", "expression of concern")
    refs = []
    for p in neufs:
        e = res.get(p)
        if not e:
            print(u"  INTROUVABLE, retiré : %s" % p)
            continue
        a = e.get("authors") or []
        t = e.get("title", "").rstrip(".")
        if not a or any(m in t.lower() for m in DOUTEUX):
            print(u"  CE N'EST PAS UNE SOURCE, retiré : %s  %s" % (p, t[:50]))
            continue
        refs.append({
            "pmid": p,
            "auteur": a[0]["name"],
            "nb": len(a),
            "revue": e.get("source", ""),
            "annee": (e.get("pubdate") or "")[:4],
            "t": t,
        })

    gr.append({"titre": TITRE, "intro": INTRO, "refs": refs})
    with io.open(str(ICI / "page_data.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        f.write(json.dumps(gr, ensure_ascii=False, indent=1) + "\n")
    print(u"\najouté : %s" % TITRE)
    print(u"  %d notices" % len(refs))
    for r in refs:
        print(u"    %-9s %-5s %-24s %s"
              % (r["pmid"], r["annee"], r["revue"][:24], r["t"][:50]))
    print(u"\n%d groupes, %d notices PubMed au total"
          % (len(gr), sum(len(g["refs"]) for g in gr)))


if __name__ == "__main__":
    main()
