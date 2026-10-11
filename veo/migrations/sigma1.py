# -*- coding: utf-8 -*-
"""Deux groupes issus de la recherche verifiee sur sigma-1, et une correction.

La page affirmait que la liaison de la DMT au sigma-1 constituait « un
chevauchement moleculaire reel » avec les dissociatifs. La recherche etablit
que l'inference est invalide. La phrase est remplacee.

Elle etablit aussi que l'effet dit « anti-amnesique », invoque pour soutenir
une remontee de souvenirs, designe tout autre chose dans son champ
d'origine — et que, lorsque l'hypothese a ete testee, le resultat l'a
contredite.
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
import time
import urllib.request

ICI = pathlib.Path(__file__).resolve().parent.parent
NCBI = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        "?db=pubmed&retmode=json&id=")

AVANT = (u"La DMT se lie au r\u00e9cepteur sigma-1 : c\u2019est publi\u00e9 dans "
         u"Science en 2009, et le sigma-1 est aussi une cible du "
         u"dextrom\u00e9thorphane et de la phencyclidine. C\u2019est un "
         u"chevauchement mol\u00e9culaire r\u00e9el, pas une image.")
APRES = (u"La DMT se lie bien au r\u00e9cepteur sigma-1, publi\u00e9 dans "
         u"<cite>Science</cite> en 2009, et le sigma-1 est aussi une cible du "
         u"dextrom\u00e9thorphane et de la phencyclidine \u2014 mais cette "
         u"parent\u00e9 ne tient pas l\u2019examen, et le groupe qui suit "
         u"explique pourquoi\u202f: la cible est un chaperon intracellulaire "
         u"promiscue, et l\u2019effet dissociatif de ces deux mol\u00e9cules ne "
         u"lui est pas attribu\u00e9.")

SIGMA = (
    u"La liaison de la DMT au récepteur sigma-1 sert deux arguments\u202f: "
    u"rapprocher la DMT des dissociatifs, et étayer un effet dit "
    u"«\u202fanti-amnésique\u202f». La recherche vérifiée contredit les deux, et "
    u"il vaut mieux le lire ici qu\u2019ailleurs.\n\n"
    u"<strong>Ce qui est établi, et c\u2019est étroit.</strong> Le travail "
    u"princeps de 2009 dans <cite>Science</cite> montre exactement trois "
    u"choses\u202f: la DMT se lie au sigma-1\u202f; elle inhibe des canaux "
    u"sodiques dans des cellules qui expriment ce récepteur\u202f; elle provoque "
    u"chez la souris une hypermobilité qui disparaît chez la souris dépourvue "
    u"du récepteur. C\u2019est la seule expérience qui relie le sigma-1 à un "
    u"comportement de la DMT — et ce comportement est une <em>hypermobilité "
    u"locomotrice chez la souris</em>, ni un effet hallucinogène, ni un effet "
    u"sur la mémoire.\n\n"
    u"<strong>Ce qu\u2019est le sigma-1.</strong> Pas un récepteur couplé à une "
    u"transduction, ni un canal\u202f: un <em>chaperon</em> du réticulum "
    u"endoplasmique aux membranes associées aux mitochondries, dont la "
    u"structure cristalline est publiée dans <cite>Nature</cite>. Les effets "
    u"cellulaires attribués à son activation par la DMT sont, sans exception, "
    u"de la cytoprotection, de la bioénergétique mitochondriale et de "
    u"l\u2019immunomodulation. Rien de psychoactif aigu.\n\n"
    u"<strong>Pourquoi le rapprochement avec les dissociatifs ne tient "
    u"pas.</strong> Le sigma-1 lie un nombre considérable de composés sans "
    u"parenté entre eux — halopéridol, fluvoxamine, progestérone, cocaïne — "
    u"parce que son pharmacophore se réduit à une amine basique flanquée de "
    u"deux régions hydrophobes. Partager une cible aussi peu discriminante ne "
    u"prédit aucune parenté clinique. Et l\u2019effet dissociatif du "
    u"dextrométhorphane et de la phencyclidine n\u2019est attribué au sigma-1 "
    u"dans aucun des travaux examinés\u202f: il est attribué au blocage du "
    u"NMDA. Un travail de 2006 sépare d\u2019ailleurs explicitement les deux "
    u"mécanismes.\n\n"
    u"<strong>Et l\u2019affinité est faible.</strong> Point de méthode "
    u"important\u202f: aucun résumé indexé ne donne de constante pour la DMT au "
    u"sigma-1 — la valeur micromolaire qui circule figure dans le corps de "
    u"l\u2019article de <cite>Science</cite>, pas dans sa notice, et doit être "
    u"relevée sur le texte intégral avant d\u2019être citée. Quatre éléments "
    u"convergents établissent néanmoins qu\u2019elle n\u2019est pas "
    u"nanomolaire, dont celui-ci\u202f: le laboratoire même de l\u2019étude "
    u"princeps a dû postuler ensuite que la DMT serait «\u202fsynthétisée "
    u"localement\u202f» pour activer efficacement le récepteur. On ne postule "
    u"une synthèse sur place que si les concentrations ambiantes ne "
    u"suffisent pas.\n\n"
    u"<strong>La DMT endogène, enfin.</strong> La question est ouverte et "
    u"activement disputée. Un travail de 2019 rapporte des concentrations "
    u"extracellulaires corticales comparables à celles des monoamines\u202f; un "
    u"travail de 2026 ne détecte aucun pool cérébral chez le rat, même sous "
    u"inhibiteur. Nichols soutient que les concentrations détectées ne "
    u"suffisent pas à produire un effet psychoactif. Un point disputé ne se "
    u"présente pas comme un acquis."
)

MEMOIRE = (
    u"Une thèse circule, reprise dans des documents destinés à des "
    u"expertises\u202f: la substance provoquerait un effet anti-amnésique qui "
    u"forcerait la remontée de souvenirs traumatiques refoulés. Elle est "
    u"fausse sur chacun de ses trois termes, et c\u2019est important à savoir "
    u"<em>avant</em> qu\u2019un expert le démontre.\n\n"
    u"<strong>Premier terme\u202f: l\u2019origine.</strong> L\u2019argument "
    u"remonte à un article de 2018 dont le titre commence par le mot "
    u"<em>Hypothesis</em>. Il ne produit aucune donnée, porte sur "
    u"l\u2019ayahuasca entière et non sur la DMT, attribue une part de "
    u"l\u2019effet aux inhibiteurs de la monoamine oxydase, et s\u2019appuie "
    u"sur des rapports subjectifs.\n\n"
    u"<strong>Deuxième terme\u202f: le mot «\u202fanti-amnésique\u202f».</strong> "
    u"Dans le champ du sigma-1, il désigne tout autre chose\u202f: la réversion "
    u"d\u2019une amnésie provoquée expérimentalement par le peptide "
    u"bêta-amyloïde, obtenue avec des agonistes sélectifs et des "
    u"neurostéroïdes, selon une courbe en cloche. C\u2019est de la "
    u"neuroprotection, et la DMT n\u2019a jamais figuré parmi les composés "
    u"testés.\n\n"
    u"<strong>Troisième terme\u202f: l\u2019épreuve des faits.</strong> "
    u"Lorsque l\u2019hypothèse a enfin été testée sur la mémoire aversive, le "
    u"résultat l\u2019a contredite deux fois. L\u2019effet passe par les "
    u"récepteurs 5-HT2A et 5-HT1A du cortex infralimbique, sans aucune "
    u"implication du sigma-1. Et il consiste en une facilitation de "
    u"l\u2019<em>extinction</em> de la peur — soit exactement l\u2019inverse "
    u"d\u2019une remontée forcée de souvenirs.\n\n"
    u"<strong>Ce qui est documenté à la place, et qui devrait inquiéter.</strong> "
    u"Les psychédéliques <em>augmentent la suggestibilité</em>\u202f: un essai "
    u"chez des volontaires sains l\u2019établit pour le LSD. Des travaux "
    u"récents rapportent par ailleurs des effets <em>délétères</em> de "
    u"l\u2019ayahuasca sur certaines performances mnésiques. Quant au "
    u"«\u202fsouvenir refoulé\u202f» lui-même, la littérature spécialisée en "
    u"psychologie de la mémoire l\u2019examine depuis trente ans et "
    u"n\u2019en soutient pas la notion.\n\n"
    u"<strong>La conséquence pratique, et elle est sévère.</strong> Invoquer "
    u"une remontée de souvenirs sous substance dans un dossier revient à "
    u"fournir à la partie adverse l\u2019argument que ces souvenirs se sont "
    u"formés dans un état de suggestibilité accrue. Un récit obtenu en "
    u"cérémonie ne vaut pas preuve, et il peut coûter la crédibilité de ce "
    u"qui l\u2019entoure. Les faits matériels, eux, ne craignent rien\u202f: "
    u"une date, une pièce, un compte rendu d\u2019hospitalisation."
)

GROUPES = [
    (u"Le récepteur sigma-1 : ce que la liaison établit, et ce qu\u2019elle ne fonde pas",
     u"Pharmacologie et mécanismes", SIGMA,
     ["19213917", "19278957", "17981125", "27042935", "8157067", "17662961",
      "16397090", "10064839", "22265729", "34023338", "40298911", "9460750",
      "41672133", "31249368", "36609666", "22371425", "39832749"]),
    (u"Ce dont on se souvient : suggestibilité, extinction, souvenirs retrouvés",
     u"Emprise, discours et dérive", MEMOIRE,
     ["29674970", "38320596", "25242255", "36069952", "39614620", "42053657",
      "33435830", "22303765", "39305969", "21555330"]),
]

DOUTEUX = ("correction to", "erratum", "corrigendum", "retraction",
           "author correction", "expression of concern")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))

    # 1. La correction de la phrase refutee, avant tout le reste.
    fait = False
    for g in gr:
        if AVANT in g["intro"]:
            g["intro"] = g["intro"].replace(AVANT, APRES)
            fait = True
            print(u"phrase corrigée dans : %s" % g["titre"])
    if not fait:
        print(u"ATTENTION : la phrase à corriger est introuvable, rien remplacé")

    # 2. Les deux groupes.
    for titre, cat, intro, pmids in GROUPES:
        if any(g["titre"] == titre for g in gr):
            print(u"déjà présent : %s" % titre)
            continue
        deja = set(r["pmid"] for g in gr for r in g["refs"])
        ou = dict((r["pmid"], g["titre"]) for g in gr for r in g["refs"])
        neufs = [p for p in pmids if p not in deja]
        for p in pmids:
            if p in deja:
                print(u"    dédoublonné : %s (%s)" % (p, ou[p][:38]))
        res = None
        for k in range(6):
            try:
                with urllib.request.urlopen(NCBI + ",".join(neufs), timeout=120) as r:
                    res = json.loads(r.read().decode("utf-8"))["result"]
                break
            except Exception as ex:
                print(u"    (NCBI occupé : %s)" % str(ex)[:40])
                time.sleep(8)
        if res is None:
            sys.exit("NCBI injoignable")
        refs = []
        for p in neufs:
            e = res.get(p)
            if not e:
                print(u"    INTROUVABLE : %s" % p)
                continue
            a = e.get("authors") or []
            t = e.get("title", "").rstrip(".")
            rev = e.get("source", "")
            if not a or not rev.strip() or any(m in t.lower() for m in DOUTEUX):
                print(u"    ECARTE : %s  %s" % (p, t[:40]))
                continue
            refs.append({"pmid": p, "auteur": a[0]["name"], "nb": len(a),
                         "revue": rev, "annee": (e.get("pubdate") or "")[:4], "t": t})
        dernier = max(i for i, g in enumerate(gr) if g.get("cat") == cat)
        gr.insert(dernier + 1,
                  {"titre": titre, "cat": cat, "intro": intro, "refs": refs})
        print(u"  ajouté : %-56s %2d notices" % (titre[:56], len(refs)))

    with io.open(str(ICI / "page_data.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        f.write(json.dumps(gr, ensure_ascii=False, indent=1) + "\n")
    print(u"\n%d groupes, %d notices PubMed"
          % (len(gr), sum(len(g["refs"]) for g in gr)))


if __name__ == "__main__":
    main()
