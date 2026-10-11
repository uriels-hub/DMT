# -*- coding: utf-8 -*-
"""Second volet de l'IMAO : ce qu'il rend dangereux autour.

Le premier groupe traitait de ce que l'inhibiteur ajoute a la pharmacologie.
Celui-ci traite de ce qu'il transforme en danger : un antidepresseur, un
aliment, un sirop contre la toux. C'est le versant le plus concret, et le
plus directement lie a une administration par des tiers qui ne demandent
rien.
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

TITRE = u"L\u2019IMAO rend dangereux ce qui ne l\u2019était pas"
CAT = u"Pharmacologie et mécanismes"

INTRO = (
    u"Inhiber la monoamine oxydase ne change pas seulement l\u2019effet du "
    u"breuvage. Cela change le statut de tout ce que la personne prend par "
    u"ailleurs, et c\u2019est le versant le plus concret du dossier.\n\n"
    u"<strong>Les médicaments d\u2019abord.</strong> La combinaison d\u2019un "
    u"inhibiteur de la monoamine oxydase et d\u2019un agent sérotoninergique est "
    u"celle dont la toxicité est la plus sévère et la mieux documentée. Une "
    u"revue systématique de 2024, portant sur plus de sept mille notices "
    u"criblées pour n\u2019en retenir que cinquante-deux, fait le point sur les "
    u"interactions des psychédéliques classiques — et conclut d\u2019abord que "
    u"l\u2019état des connaissances est <em>limité</em>. Les antidépresseurs "
    u"sérotoninergiques sont les premiers concernés, mais la liste déborde la "
    u"psychiatrie\u202f: le dextrométhorphane des sirops contre la toux, le "
    u"tramadol, les triptans de la migraine, et jusqu\u2019au linézolide, un "
    u"antibiotique qui se trouve être un inhibiteur de la monoamine oxydase et "
    u"dont les cas de syndrome sérotoninergique font l\u2019objet de "
    u"publications régulières.\n\n"
    u"Ce point n\u2019est pas théorique dans un contexte rituel. Les personnes "
    u"qu\u2019on amène à ces cérémonies sont souvent celles qui vont mal, "
    u"c\u2019est-à-dire précisément celles qui ont le plus de chances "
    u"d\u2019être sous traitement sérotoninergique. Et personne ne le demande.\n\n"
    u"<strong>Les aliments ensuite, et c\u2019est le «\u202feffet "
    u"fromage\u202f».</strong> Sous inhibiteur de la monoamine oxydase, la "
    u"tyramine alimentaire n\u2019est plus dégradée et provoque des poussées "
    u"hypertensives, avec un risque d\u2019hémorragie intracérébrale et de "
    u"décès. Les recommandations diététiques qui encadrent ces médicaments "
    u"découlent entièrement de là.\n\n"
    u"<strong>Une nuance importante, et elle joue en sens inverse.</strong> "
    u"L\u2019harmine est un inhibiteur <em>réversible</em>. Les inhibiteurs "
    u"réversibles de la MAO-A comportent un risque tyraminique nettement plus "
    u"faible que les irréversibles, et c\u2019est pour cela qu\u2019ils ont été "
    u"développés. La réversibilité est une marge de sécurité réelle, et une "
    u"page honnête doit la porter.\n\n"
    u"<strong>Et voici ce que je n\u2019attendais pas.</strong> La <em>dieta</em> "
    u"amazonienne — des semaines de restrictions alimentaires, sociales et "
    u"comportementales, documentée comme méthode à part entière dans la "
    u"littérature ethnopharmacologique — interdit précisément les aliments "
    u"fermentés, les fromages affinés, la charcuterie, l\u2019alcool. "
    u"C\u2019est, trait pour trait, un régime pauvre en tyramine. La tradition "
    u"a donc encodé empiriquement l\u2019interaction que la pharmacologie a "
    u"décrite deux siècles plus tard, sans en formuler la raison. "
    u"L\u2019observation vaut dans les deux sens\u202f: elle crédite le savoir "
    u"traditionnel d\u2019une cohérence réelle, et elle établit que "
    u"l\u2019interaction est assez sérieuse pour avoir été découverte sans "
    u"laboratoire.\n\n"
    u"<strong>Le revers de la même pratique.</strong> Ces mêmes restrictions, "
    u"prolongées, ne sont pas sans conséquence nutritionnelle, et la revue de "
    u"référence sur la <em>dieta</em> note que la méthode reste «\u202flargement "
    u"inexplorée\u202f» du point de vue clinique. AUCUNE ÉTUDE INDEXÉE NE MESURE "
    u"L\u2019ÉTAT NUTRITIONNEL DES PERSONNES QUI LA SUIVENT. Le groupe sur "
    u"l\u2019atteinte radiculaire explique pourquoi cela mériterait un bilan "
    u"sanguin."
)

PMIDS = [
    "37982394",   # Halman, interactions des psychedeliques : revue systematique
    "40541320",   # Vogt, pharmacologie clinique
    "39932284",   # Wali, linezolide et syndrome serotoninergique
    "34414219",   # Calvi, antidepresseurs et pression arterielle
    "2666453",    # Brown, l'interaction IMAO-tyramine
    "6394124",    # Sullivan, regime et IMAO : reexamen
    "8430214",    # Waldmeier, aspects nouveaux des inhibiteurs reversibles
    "1546143",    # Haefely, moclobemide, prototype de RIMA
    "29516165",   # Ramsay, cinetique, mecanisme et inhibition de la MAO
    "34933085",   # Berlowitz, la dieta comme methode
    "25877327",   # Araujo, le monde hallucinogene des tryptamines
    "33291798",   # Malaca, toxicologie et analyse des tryptamines
]

DOUTEUX = ("correction to", "erratum", "corrigendum", "retraction",
           "author correction", "expression of concern")


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
            print(u"  dédoublonné : %s déjà dans « %s »" % (p, ou[p][:42]))

    res = None
    for k in range(6):
        try:
            with urllib.request.urlopen(NCBI + ",".join(neufs), timeout=120) as r:
                res = json.loads(r.read().decode("utf-8"))["result"]
            break
        except Exception as ex:
            print(u"  (NCBI occupé : %s)" % ex)
            time.sleep(7)
    if res is None:
        sys.exit("NCBI injoignable")

    refs = []
    for p in neufs:
        e = res.get(p)
        if not e:
            print(u"  INTROUVABLE : %s" % p)
            continue
        a = e.get("authors") or []
        t = e.get("title", "").rstrip(".")
        rev = e.get("source", "")
        if not a or not rev.strip() or any(m in t.lower() for m in DOUTEUX):
            print(u"  ECARTE : %s  %s" % (p, t[:44]))
            continue
        refs.append({"pmid": p, "auteur": a[0]["name"], "nb": len(a),
                     "revue": rev, "annee": (e.get("pubdate") or "")[:4], "t": t})

    dernier = max(i for i, g in enumerate(gr) if g.get("cat") == CAT)
    gr.insert(dernier + 1, {"titre": TITRE, "cat": CAT, "intro": INTRO, "refs": refs})
    with io.open(str(ICI / "page_data.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        f.write(json.dumps(gr, ensure_ascii=False, indent=1) + "\n")

    print(u"\najouté : %s\n  %d notices" % (TITRE, len(refs)))
    for r in refs:
        print(u"    %-9s %-5s %-26s %s"
              % (r["pmid"], r["annee"], r["revue"][:26], r["t"][:42]))
    print(u"\n%d groupes, %d notices PubMed"
          % (len(gr), sum(len(g["refs"]) for g in gr)))


if __name__ == "__main__":
    main()
