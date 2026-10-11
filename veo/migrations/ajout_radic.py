# -*- coding: utf-8 -*-
"""Ajoute le groupe sur l'atteinte radiculaire.

Ce groupe existe pour une raison precise : un argument medico-legal circule,
selon lequel une atteinte radiculaire a l'electromyogramme prouverait
l'origine toxique d'un trouble. Il ne le prouve pas, et le dire ici vaut
mieux que de le laisser demonter par un expert.

Le groupe porte donc les quatre choses dans l'ordre :
  ce que l'EMG distingue   radiculopathie et polyneuropathie n'ont pas la
                           meme signification causale
  ce qui l'expliquerait    le syndrome des loges, les carences
  la frequence de base     ce que la partie adverse opposera, et son contrepoids
  ce qui n'existe pas      ecrit en capitales, comme pour les autres groupes
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

TITRE = u"Une atteinte radiculaire : ce qu\u2019elle prouve, et ce qu\u2019elle ne prouve pas"
CAT = u"Ce que les examens trouvent"

INTRO = (
    u"Un argument circule, et il faut le traiter de face : une atteinte "
    u"neurogène d\u2019allure radiculaire à l\u2019électromyogramme prouverait "
    u"l\u2019origine toxique d\u2019un trouble, au motif qu\u2019«\u202fune maladie "
    u"psychiatrique ne provoque jamais cela\u202f». La seconde proposition est vraie "
    u"et ne sert à rien : personne ne la soutient. La première est fausse.\n\n"
    u"<strong>Ce que le tracé distingue.</strong> Une cause toxique ou "
    u"métabolique produit une <em>polyneuropathie</em> : longueur-dépendante, "
    u"symétrique, distale d\u2019abord. Une atteinte <em>radiculaire</em> "
    u"multi-étagée et latéralisée est le profil compressif et dégénératif, qui "
    u"désigne le rachis. Ce sont deux lectures opposées du même examen, et c\u2019est "
    u"la seconde, non la première, qui plaide contre une origine toxique. Devant un "
    u"compte rendu, les lignes qui comptent sont les vitesses de conduction "
    u"distales, les amplitudes sensitives, les ondes F et les réponses surales.\n\n"
    u"<strong>Ce qui expliquerait réellement une atteinte radiculaire après une "
    u"intoxication.</strong> Une voie tient de bout en bout : une toxicité "
    u"sérotoninergique produit une hyperactivité musculaire, donc une "
    u"rhabdomyolyse, donc un gonflement dans une loge inextensible, donc un "
    u"<em>syndrome des loges</em>. Or le syndrome des loges fessier est "
    u"classiquement décrit chez des personnes retrouvées après une immobilité "
    u"prolongée en conscience altérée, et il comprime le nerf sciatique — dont "
    u"l\u2019atteinte, à l\u2019électromyogramme, <em>mime une radiculopathie L5-S1</em>. "
    u"Ce mécanisme laisse des traces datables : douleur, gonflement, urines "
    u"foncées, créatine phosphokinase élevée.\n\n"
    u"<strong>Une seconde voie, testable aujourd\u2019hui.</strong> Les neuropathies "
    u"nutritionnelles. Les régimes restrictifs prolongés et les vomissements "
    u"répétés appauvrissent en vitamine B12 et en thiamine ; et la vitamine B6 "
    u"donne une neuropathie <em>par excès autant que par carence</em>, ce que la "
    u"consommation de compléments rend non théorique. Un bilan sanguin tranche, "
    u"pour un coût négligeable.\n\n"
    u"<strong>Ce que la partie adverse opposera, et il faut le savoir.</strong> La "
    u"dégénérescence discale est quasi universelle : une revue systématique de 2015 "
    u"la trouve chez 37\u202f% des sujets <em>asymptomatiques</em> de vingt ans et "
    u"96\u202f% à quatre-vingts, et une étude du <cite>New England Journal of "
    u"Medicine</cite> de 1994 relève un bombement discal chez 52\u202f% de personnes "
    u"sans aucune douleur. Un profil cervical et lombo-sacré chez un adulte est la "
    u"trouvaille la plus attendue de la neurologie. Le contrepoids existe pourtant, "
    u"et il est du même auteur la même année : la dégénérescence est plus fréquente "
    u"chez les personnes qui ont mal que chez les témoins. «\u202fC\u2019est "
    u"banal\u202f» ne signifie donc pas «\u202fc\u2019est sans rapport\u202f» ; cela "
    u"signifie que cela ne peut pas porter seul une causalité.\n\n"
    u"<strong>Ce qui reste défendable.</strong> Les récepteurs 5-HT2A participent à "
    u"la douleur radiculaire — un antagoniste 5-HT2A a été étudié dans la hernie "
    u"discale lombaire. Avec l\u2019axe sérotoninergique du tonus musculaire traité "
    u"ailleurs sur cette page, cela soutient une proposition mesurée, et une seule\u202f: "
    u"un état dégénératif latent et asymptomatique a pu être rendu symptomatique. "
    u"Pas qu\u2019une substance ait créé la lésion.\n\n"
    u"<strong>Et ce qui n\u2019existe pas.</strong> AUCUN TRAVAIL INDEXÉ NE RELIE LES "
    u"BÊTA-CARBOLINES AU MOTONEURONE NI À LA CORNE ANTÉRIEURE — la recherche rend "
    u"trois résultats, dont aucun ne porte sur ce lien, et l\u2019un décrit même la "
    u"harmine comme protectrice du transporteur du glutamate. AUCUN CAS PUBLIÉ DE "
    u"RADICULOPATHIE ATTRIBUÉE À L\u2019AYAHUASCA. AUCUNE DOCUMENTATION INDEXÉE DE "
    u"CARENCE NUTRITIONNELLE CHEZ LES PRATIQUANTS."
)

PMIDS = [
    # Lire le trace : ce que chaque profil veut dire
    "23524070",   # Dillingham, evaluer un patient suspect de radiculopathie
    "33320513",   # Castelli, neuropathie peripherique : evaluation et diagnostic differentiel
    "8129590",    # Ellenberg, radiculopathie cervicale
    # Le syndrome des loges : la voie qui tient de bout en bout
    "33002399",   # Cepkova, syndrome des loges aigu
    "19492552",   # Henson, syndrome des loges fessier
    "16813640",   # Hayden, syndrome des loges fessier
    "7978606",    # Prynn, syndrome des loges fessier
    "40975781",   # Papageorgiou, loges fessier et paralysie du sciatique
    "26862401",   # Alobaidi, loges de cuisse compliquee d'atteinte sciatique
    "32091738",   # Mauffrey, syndrome des loges par positionnement
    "33936907",   # Ejikeme, neuropathie peripherique apres rhabdomyolyse
    # Les carences, et l'exces
    "31837157",   # Gwathmey, neuropathies nutritionnelles : la revue de reference
    "33912895",   # Hadtstein, neuropathie induite par la vitamine B6
    "37447150",   # Muhamad, role de la B6 dans la neuropathie peripherique
    "38673453",   # Obeid, carence en B12 : diagnostic et prise en charge
    "27169753",   # Harrington, evaluation biologique du statut en B12
    # La frequence de base, et son contrepoids
    "25430861",   # Brinjikji, degenerescence rachidienne chez l'asymptomatique
    "26359154",   # Brinjikji, plus frequente chez ceux qui ont mal que chez les temoins
    "8208267",    # Jensen, NEJM : IRM lombaire chez des personnes sans douleur
    "3588931",    # Teresi, degenerescence cervicale asymptomatique
    # La serotonine dans la douleur radiculaire
    "17268262",   # Hashizume, sarpogrelate, antagoniste 5-HT2A, dans Spine
    "15871484",   # Kanayama, 5-HT2A et hernie discale lombaire
    "18496345",   # Kato, 5-HT et comportement douloureux
]

DOUTEUX = ("correction to", "erratum", "corrigendum", "retraction",
           "author correction", "expression of concern")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    if any(g["titre"] == TITRE for g in gr):
        sys.exit(u"groupe déjà présent")
    if CAT not in set(g.get("cat") for g in gr):
        sys.exit(u"catégorie inconnue : %s" % CAT)

    deja = set(r["pmid"] for g in gr for r in g["refs"])
    ou = dict((r["pmid"], g["titre"]) for g in gr for r in g["refs"])
    neufs = [p for p in PMIDS if p not in deja]
    for p in PMIDS:
        if p in deja:
            print(u"  déjà sur la page, retiré : %s  [%s]" % (p, ou[p][:44]))

    with urllib.request.urlopen(NCBI + ",".join(neufs), timeout=120) as r:
        res = json.loads(r.read().decode("utf-8"))["result"]

    refs = []
    for p in neufs:
        e = res.get(p)
        if not e:
            print(u"  INTROUVABLE, retiré : %s" % p)
            continue
        a = e.get("authors") or []
        t = e.get("title", "").rstrip(".")
        if not a or any(m in t.lower() for m in DOUTEUX):
            print(u"  CE N'EST PAS UNE SOURCE, retiré : %s  %s" % (p, t[:46]))
            continue
        refs.append({
            "pmid": p, "auteur": a[0]["name"], "nb": len(a),
            "revue": e.get("source", ""), "annee": (e.get("pubdate") or "")[:4],
            "t": t,
        })

    # Le groupe se range a la fin de sa categorie, pas a la fin du fichier :
    # l'ordre du fichier est l'ordre de rendu.
    dernier = max(i for i, g in enumerate(gr) if g.get("cat") == CAT)
    gr.insert(dernier + 1, {"titre": TITRE, "cat": CAT, "intro": INTRO, "refs": refs})

    with io.open(str(ICI / "page_data.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        f.write(json.dumps(gr, ensure_ascii=False, indent=1) + "\n")

    print(u"\najouté dans « %s » : %d notices\n" % (CAT, len(refs)))
    for r in refs:
        print(u"    %-9s %-5s %-24s %s"
              % (r["pmid"], r["annee"], r["revue"][:24], r["t"][:46]))
    print(u"\n%d groupes, %d notices PubMed"
          % (len(gr), sum(len(g["refs"]) for g in gr)))
    # L'ordre par categorie doit rester un bloc par categorie, sans entrelacement.
    vus, casse = [], []
    for g in gr:
        c = g.get("cat")
        if not vus or vus[-1] != c:
            if c in vus:
                casse.append(c)
            vus.append(c)
    print(u"  ordre des catégories : %s" % (u"intact" if not casse
                                            else u"ENTRELACE : %s" % casse))


if __name__ == "__main__":
    main()
