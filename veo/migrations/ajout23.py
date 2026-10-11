# -*- coding: utf-8 -*-
"""Ajoute deux groupes à la page publique de TOXICOSQUEROS.

23  La DMT est-elle un dissociatif ?   répond à une question de classification
24  Takiwasi                           ce qu'écrit une source gouvernementale

Les notices PubMed ne sont pas rédigées : seuls les PMID sont écrits ici, et
maj.py va chercher auteur, revue, année et titre à la source. Les entrées hors
PubMed portent leur libellé, parce qu'un rapport ministériel n'a pas de PMID.
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

DISSO = (
    u"Non, et la nuance vaut d\u2019être posée, parce qu\u2019elle se retourne "
    u"dans les deux sens.\n\n"
    u"Un dissociatif se définit par son récepteur : il bloque le NMDA. C\u2019est "
    u"vrai de la kétamine, de la phencyclidine, du dextrométhorphane, du protoxyde "
    u"d\u2019azote. La DMT n\u2019y touche pas. Elle agit en agoniste du récepteur "
    u"5-HT2A, et la preuve est expérimentale : bloquer ce seul récepteur par la "
    u"kétansérine supprime l\u2019effet psychédélique chez l\u2019homme. Mieux, sur "
    u"le test de discrimination animale, les hallucinogènes ne se contentent pas de "
    u"différer de la phencyclidine, ils antagonisent sa discrimination. La CIM-11 "
    u"tire la même ligne, en séparant le 6C49 des hallucinogènes du 6C4D des "
    u"dissociatifs.\n\n"
    u"Et pourtant trois choses tiennent dans l\u2019autre sens. La DMT se lie au "
    u"récepteur sigma-1 : c\u2019est publié dans Science en 2009, et le sigma-1 est "
    u"aussi une cible du dextrométhorphane et de la phencyclidine. C\u2019est un "
    u"chevauchement moléculaire réel, pas une image. Ensuite, les deux classes "
    u"convergent en aval sur le même désordre, l\u2019excès de glutamate cortical, "
    u"par deux portes opposées : l\u2019antagoniste NMDA désinhibe les interneurones, "
    u"l\u2019agoniste 5-HT2A excite directement les cellules pyramidales. Enfin la "
    u"phénoménologie se recouvre massivement : la DMT est le meilleur modèle "
    u"pharmacologique connu de l\u2019expérience de mort imminente, et la "
    u"dépersonnalisation figure parmi ses effets documentés.\n\n"
    u"Ce qu\u2019il faut en retenir pour une discussion contradictoire. "
    u"L\u2019argument «\u202fce n\u2019est pas un dissociatif, donc pas de "
    u"dépersonnalisation\u202f» est faux : la dépersonnalisation ne demande pas le "
    u"NMDA. Mais l\u2019affirmation inverse, «\u202fla DMT est un dissociatif\u202f», "
    u"se fait démonter en deux lignes par un pharmacologue, et fait perdre le reste. "
    u"La formulation qui tient est la troisième : la DMT produit des effets "
    u"dissociatifs sans être un dissociatif."
)

TAKI = (
    u"Ce groupe sort de la pharmacologie pour une raison simple : le centre "
    u"Takiwasi, à Tarapoto au Pérou, est nommé dans un rapport officiel français, "
    u"et il recrute en France.\n\n"
    u"Le rapport de la MIVILUDES au Premier ministre pour 2005 lui consacre un "
    u"développement. Il le décrit comme un «\u202fcentre de traitement des "
    u"toxicomanies à base de méthodes chamaniques créé en 1992 au Pérou par un "
    u"médecin français, le Docteur Jacques Mabit\u202f». Il note que son fondateur "
    u"n\u2019a jamais été condamné, et que cela «\u202fne met pas fin à de sérieuses "
    u"inquiétudes\u202f». Il écrit que «\u202fla violence des méthodes utilisées pour "
    u"le sevrage des toxicomanes interroge\u202f» par les risques courus par des "
    u"patients très vulnérables, qu\u2019aucune statistique fiable n\u2019existe sur "
    u"le taux de réussite, et que le problème principal est la dérive du sevrage "
    u"vers une «\u202fmédecine de l\u2019âme\u202f» ouverte à d\u2019autres publics, "
    u"dont des malades du cancer déclarés incurables. Il identifie enfin le relais "
    u"promotionnel français de l\u2019époque, une association lyonnaise.\n\n"
    u"Sur l\u2019argent public français, voici l\u2019état exact de ce qui est "
    u"vérifiable. Dans sa propre réponse à la thèse de David Dupuis, publiée sur son "
    u"site, Takiwasi écrit que la Délégation générale à la lutte contre les drogues, "
    u"«\u202fdépendance du Ministère des Affaires Étrangères du gouvernement "
    u"français\u202f», a «\u202ffinancé en partie pendant 5 ans les travaux de "
    u"recherche\u202f» de Jacques Mabit préalables à la création du centre. "
    u"C\u2019est le centre lui-même qui l\u2019écrit, et il le présente comme une "
    u"caution. Cela établit un financement public français de la recherche qui a "
    u"précédé le centre, soit autour de 1987-1992 si l\u2019on compte cinq ans avant "
    u"sa création. Cela n\u2019établit ni un financement du centre lui-même, que "
    u"Takiwasi conteste, ni aucun montant : aucune source publique accessible ne "
    u"chiffre cette aide. Le même document nie une contribution des Nations unies et "
    u"affirme que le terrain fut acquis sur fonds propres.\n\n"
    u"Reste un point qui relève du groupe sur les études menées par des adeptes : "
    u"plusieurs des publications indexées qui évaluent favorablement ce centre sont "
    u"signées par des auteurs qui y sont affiliés."
)

GROUPES = [
    {
        "titre": u"La DMT est-elle un dissociatif ?",
        "intro": DISSO,
        "pmids": [
            "9875725",    # Vollenweider, psilocybine via le 5-HT2A : necessite du recepteur
            "29555857",   # Preller, role du 5-HT2A, blocage par la ketanserine
            "38720072",   # Warren, Nature, pharmacologie structurale du 5-MeO-DMT
            "10788761",   # West, les hallucinogenes antagonisent la discrimination du PCP
            "29945898",   # Zanos, pharmacologie de la ketamine : la definition NMDA
            "30105474",   # Wallach, substances nouvelles derivees de la phencyclidine
            "19213917",   # Fontanilla, Science : la DMT regule le recepteur sigma-1
            "23619992",   # Frecska, role de la DMT par le sigma-1
            "29095071",   # Nichols, DMT et glande pineale : separer le fait du mythe
            "28238186",   # Llado-Pelfort, effets des hallucinogenes sur l'activite neuronale
            "34565579",   # Aleksandrova, neuroplasticite : un mecanisme convergent
            "36630309",   # Davoudian, regions cerebrales partagees et distinctes
            "30174629",   # Timmermann, la DMT modelise l'experience de mort imminente
            "39220326",   # Martial, comparaison intra-sujet mort imminente / psychedelique
            "36786290",   # Stoliker, dissolution de l'ego
            "33009457",   # Doss, salvinorine A : l'hallucinogene dissociatif atypique
        ],
    },
    {
        "titre": u"Takiwasi : ce qu\u2019écrit la MIVILUDES, et d\u2019où vient l\u2019argent",
        "intro": TAKI,
        "pmids": [
            "31043116",   # Berlowitz, effets a court terme, Takiwasi
            "32800077",   # Berlowitz, qui se tourne vers la medecine amazonienne
            "37948338",   # Mendive, une medecine ancienne pour une maladie moderne
            "34093190",   # Rush, protocole d'evaluation du traitement par ayahuasca
            "37615330",   # Rush, ATOP : resultats a un an
            "33717431",   # O'Shaughnessy, changements en cours de traitement
            "30281759",   # Dupuis, des pratiques en quete de legitimite
            "36263513",   # Dupuis, culture, contexte et ethique
            "34887799",   # Dupuis, les psychedeliques comme vecteurs de croyance
            "36367797",   # Dupuis, la socialisation des hallucinations
            "16149335",   # Winkelman, tourisme de drogue ou guerison spirituelle
            "39374048",   # Gearin, guerir avec l'ayahuasca, la plante maitresse
        ],
    },
]

AUTRES = [
    {
        "grp": u"Rapport officiel français",
        "id": u"MIVILUDES 2005",
        "u": ("https://www.miviludes.interieur.gouv.fr/sites/miviludes/files/"
              "medias/documents/2025-07/Rapport_MIVILUDES_2005-2.pdf"),
        "t": (u"Rapport au Premier ministre : Takiwasi nommé, «\u202fla violence des "
              u"méthodes utilisées pour le sevrage\u202f» et la dérive vers une "
              u"«\u202fmédecine de l\u2019âme\u202f»."),
        "a": (u"Mission interministérielle de vigilance et de lutte contre les "
              u"dérives sectaires"),
        "s": u"Rapport au Premier ministre, année 2005",
        "y": u"2006",
    },
    {
        "grp": u"La source le dit elle-même",
        "id": u"takiwasi.com, réponse à D. Dupuis",
        "u": ("https://www.takiwasi.com/docs/arti_fra/"
              "elements-critiques-these-david-dupuis.pdf"),
        "t": (u"Takiwasi écrit que la Délégation générale à la lutte contre les "
              u"drogues, dépendant du ministère des Affaires étrangères, a "
              u"«\u202ffinancé en partie pendant 5 ans\u202f» les recherches "
              u"préalables à la création du centre."),
        "a": (u"Centre Takiwasi, «\u202fÉléments critiques à la thèse doctorale de "
              u"David Dupuis\u202f»"),
        "s": u"takiwasi.com",
        "y": u"s. d.",
    },
    {
        "grp": u"Thèse de référence",
        "id": u"theses.fr 2016EHES0708",
        "u": "https://theses.fr/2016EHES0708",
        "t": (u"Les murmures de l\u2019ayahuasca : parcours rituel et transmission "
              u"culturelle à Takiwasi. Enquête de terrain dans le centre, thèse "
              u"soutenue à l\u2019EHESS."),
        "a": u"Dupuis, D., sous la direction de Philippe Descola",
        "s": u"EHESS",
        "y": u"2016",
    },
    {
        "grp": u"Association reconnue d\u2019utilité publique",
        "id": u"UNADFI, Centre Takiwasi",
        "u": "https://www.unadfi.org/actualites/groupes-et-mouvances/centre-takiwasi/",
        "t": (u"Fiche de l\u2019UNADFI sur le centre, reprenant les réserves du "
              u"rapport de la MIVILUDES et la vente de produits dits naturels."),
        "a": u"UNADFI",
        "s": u"unadfi.org, rubrique Groupes et mouvances",
        "y": u"2014",
    },
    {
        "grp": u"Juridiction française",
        "id": u"CE, 18 décembre 2024, n° 487157",
        "u": ("https://conseil-etat.fr/fr/arianeweb/CRP/conclusion/"
              "2024-12-18/487157?download_pdf="),
        "t": (u"Conclusions du rapporteur public : le classement de l\u2019ayahuasca "
              u"parmi les stupéfiants est maintenu, et les retraites sont citées "
              u"comme objet d\u2019une «\u202fsurveillance renforcée\u202f» de la "
              u"MIVILUDES."),
        "a": u"Janicot, T., rapporteur public, séance du 29 novembre 2024",
        "s": u"Conseil d\u2019État, 1re et 4e chambres réunies",
        "y": u"2024",
    },
]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    au = json.loads((ICI / "page_autres.json").read_text(encoding="utf-8"))

    deja = set(r["pmid"] for g in gr for r in g["refs"])
    titres = set(g["titre"] for g in gr)
    ids = set(a["id"] for a in au)

    for spec in GROUPES:
        if spec["titre"] in titres:
            print(u"déjà présent, ignoré : %s" % spec["titre"])
            continue
        neufs = [p for p in spec["pmids"] if p not in deja]
        doubles = [p for p in spec["pmids"] if p in deja]
        if doubles:
            print(u"  déjà ailleurs sur la page, retirés : %s" % ", ".join(doubles))
        with urllib.request.urlopen(NCBI + ",".join(neufs), timeout=120) as r:
            res = json.loads(r.read().decode("utf-8"))["result"]
        refs = []
        for p in neufs:
            e = res.get(p)
            if not e:
                print(u"  INTROUVABLE, retiré : %s" % p)
                continue
            a = e.get("authors") or []
            refs.append({
                "pmid": p,
                "auteur": a[0]["name"] if a else "?",
                "nb": len(a),
                "revue": e.get("source", ""),
                "annee": (e.get("pubdate") or "")[:4],
                "t": e.get("title", "").rstrip("."),
            })
        gr.append({"titre": spec["titre"], "intro": spec["intro"], "refs": refs})
        print(u"ajouté : %-46s %2d notices" % (spec["titre"][:46], len(refs)))

    for a in AUTRES:
        if a["id"] in ids:
            print(u"déjà présent, ignoré : %s" % a["id"])
            continue
        au.append(a)
        print(u"ajouté hors PubMed : %s" % a["id"])

    for nom, obj in (("page_data.json", gr), ("page_autres.json", au)):
        with io.open(str(ICI / nom), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")
    print(u"\n%d groupes, %d notices PubMed, %d hors PubMed, %d au total"
          % (len(gr), sum(len(g["refs"]) for g in gr), len(au),
             sum(len(g["refs"]) for g in gr) + len(au)))


if __name__ == "__main__":
    main()
