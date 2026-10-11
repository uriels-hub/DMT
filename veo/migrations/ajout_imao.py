# -*- coding: utf-8 -*-
"""Ajoute le groupe sur ce que l'IMAO ajoute a la DMT.

Le tableau d'affinite de la page decrit la DMT SEULE. Ce n'est pas
l'exposition reelle. Ce groupe porte la difference, et elle est grande :
l'inhibiteur n'est pas un simple vehicule, il ajoute un second agoniste.

La chaine valvulaire qui en decoule ne passe pas par la liaison de la DMT au
5-HT2B. Elle passe par la serotonine endogene, qui est le substrat prefere de
la MAO-A et l'agoniste naturel du 5-HT2B.
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

TITRE = u"Ce que l\u2019IMAO ajoute : la sérotonine devient le second agoniste"
CAT = u"Pharmacologie et mécanismes"

INTRO = (
    u"Le tableau d\u2019affinité du groupe précédent décrit la DMT <em>seule</em>. "
    u"Ce n\u2019est pas l\u2019exposition réelle, et la différence n\u2019est pas "
    u"une nuance.\n\n"
    u"<strong>L\u2019inhibiteur ne fait pas que livrer la DMT.</strong> La "
    u"sérotonine est le substrat <em>préféré</em> de la monoamine oxydase A. "
    u"Inhiber cette enzyme élève donc la sérotonine endogène, dans le cerveau "
    u"comme à la périphérie. Au moment où la DMT agit, les mêmes récepteurs "
    u"voient une sérotonine élevée — et la sérotonine a pour ses propres "
    u"récepteurs une affinité bien supérieure à celle de la DMT. Le tableau "
    u"d\u2019affinité ne décrit donc qu\u2019un des deux agonistes présents.\n\n"
    u"<strong>Pour la question valvulaire, cela déplace tout l\u2019argument, et "
    u"le renforce.</strong> La voie n\u2019a plus besoin que la DMT se lie "
    u"elle-même au 5-HT2B. Des rats recevant de la sérotonine en injection "
    u"quotidienne pendant trois mois développent une hypersérotoninémie "
    u"multipliée par plus de dix et, pour six sur dix d\u2019entre eux, un "
    u"échocardiogramme pathologique — insuffisance aortique ou pulmonaire, avec "
    u"des plaques faites de myofibroblastes dans une matrice de collagène, "
    u"c\u2019est-à-dire l\u2019histologie de la maladie carcinoïde. Ce travail "
    u"est paru dans <cite>Circulation</cite>. La preuve de concept humaine "
    u"existe d\u2019ailleurs depuis longtemps sous le nom de cardiopathie "
    u"carcinoïde\u202f: des tumeurs qui sécrètent de la sérotonine fibrosent les "
    u"valves.\n\n"
    u"<strong>Et il existe une donnée sur l\u2019ayahuasca elle-même.</strong> "
    u"Quatorze jours d\u2019administration chez le rat suffisent à modifier la "
    u"paroi de l\u2019aorte\u202f: aplatissement et étirement des cellules "
    u"musculaires lisses, réorganisation du collagène et des fibres élastiques, "
    u"et à la dose la plus forte une augmentation significative de "
    u"l\u2019épaisseur de la média rapportée au diamètre de la lumière. Les "
    u"auteurs — qui appartiennent au courant favorable à la recherche sur "
    u"l\u2019ayahuasca — concluent eux-mêmes qu\u2019il faut étudier la fonction "
    u"cardiovasculaire des consommateurs au long cours.\n\n"
    u"<strong>Chez l\u2019homme, une seule mesure périphérique existe.</strong> "
    u"Callaway et ses collègues ont trouvé en 1994, chez des buveurs réguliers "
    u"d\u2019ayahuasca, un nombre accru de sites de transport de la sérotonine "
    u"sur les plaquettes, à constante de dissociation inchangée. Les auteurs "
    u"assortissent eux-mêmes ce résultat d\u2019une mise en garde qu\u2019il faut "
    u"reprendre\u202f: un tel changement ne doit pas être interprété comme le "
    u"signe d\u2019une maladie neurologique ou psychiatrique en formation.\n\n"
    u"<strong>Trois mécanismes sérotoninergiques, pas un.</strong> "
    u"L\u2019inhibition de la MAO-A, l\u2019inhibition de la recapture de la "
    u"sérotonine par la tétrahydroharmine, et l\u2019agonisme direct de la DMT. "
    u"C\u2019est la combinaison dont le gradient de toxicité est le plus raide, "
    u"et elle tient dans une seule tasse.\n\n"
    u"<strong>Les bêta-carbolines ne sont pas un véhicule inerte.</strong> Hors "
    u"MAO, elles inhibent la kinase DYRK1A — au point que l\u2019harmine est "
    u"aujourd\u2019hui développée pour faire proliférer les cellules bêta "
    u"pancréatiques —, allongent la période de l\u2019horloge circadienne et "
    u"produisent le tremblement de référence du laboratoire, points traités "
    u"ailleurs sur cette page.\n\n"
    u"<strong>Les limites, et elles comptent.</strong> Le travail de "
    u"<cite>Circulation</cite> porte sur des rats recevant de la sérotonine tous "
    u"les jours pendant trois mois\u202f: l\u2019exposition rituelle est "
    u"intermittente, et l\u2019harmine est un inhibiteur <em>réversible</em>, ce "
    u"qui est une différence réelle et plutôt rassurante. L\u2019étude sur "
    u"l\u2019aorte porte sur quatorze jours chez le rat. AUCUNE ÉTUDE "
    u"ÉCHOCARDIOGRAPHIQUE N\u2019A ÉTÉ CONDUITE CHEZ DES CONSOMMATEURS HUMAINS. "
    u"Ce groupe établit un mécanisme plausible et documenté par étapes, pas un "
    u"dommage constaté."
)

PMIDS = [
    "35600851",   # Berlowitz, inhibition de la MAO par les beta-carbolines vegetales
    "33114119",   # Brito-da-Costa, toxicocinetique et toxicodynamie des alcaloides
    "15781732",   # Gustafsson, Circulation : la serotonine seule fibrose les valves
    "15831837",   # Setola, determinants moleculaires des valvulopathogenes
    "33208036",   # Song, heterodimerisation du 5-HT2B
    "39032441",   # Dumotier, attenuer le risque cardiaque lie a l'agonisme 5-HT2B
    "39328381",   # Ross, cardiopathie carcinoide
    "25714595",   # Pitol, l'ayahuasca modifie la structure de l'aorte du rat
    "7892432",    # Callaway, transporteurs plaquettaires chez les buveurs
    "37874530",   # Wsol, securite cardiovasculaire de la medecine psychedelique
    "38985854",   # Rosselot, harmine et proliferation des cellules beta
    "32462403",   # Correa-Saez, mise a jour sur DYRK1A
    "32660098",   # Santos, variabilite du profil en beta-carbolines de la liane
]

DOUTEUX = ("correction to", "erratum", "corrigendum", "retraction",
           "author correction", "expression of concern")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    if any(g["titre"] == TITRE for g in gr):
        sys.exit(u"groupe déjà présent")
    if CAT not in set(g.get("cat") for g in gr):
        sys.exit(u"catégorie inconnue")

    deja = set(r["pmid"] for g in gr for r in g["refs"])
    ou = dict((r["pmid"], g["titre"]) for g in gr for r in g["refs"])
    neufs = [p for p in PMIDS if p not in deja]
    for p in PMIDS:
        if p in deja:
            print(u"  dédoublonné : %s déjà dans « %s »" % (p, ou[p][:42]))

    res = None
    for essai in range(5):
        try:
            with urllib.request.urlopen(NCBI + ",".join(neufs), timeout=120) as r:
                res = json.loads(r.read().decode("utf-8"))["result"]
            break
        except Exception as ex:
            print(u"  (NCBI occupé, nouvel essai : %s)" % ex)
            time.sleep(6)
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
              % (r["pmid"], r["annee"], r["revue"][:26], r["t"][:44]))
    print(u"\n%d groupes, %d notices PubMed"
          % (len(gr), sum(len(g["refs"]) for g in gr)))


if __name__ == "__main__":
    main()
