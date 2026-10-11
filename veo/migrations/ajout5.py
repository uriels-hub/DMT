# -*- coding: utf-8 -*-
"""Ajoute cinq groupes : la non-linearite de la dose, et les quatre themes
que l'audit avait trouves absents de la page.

Les PMID des quatre derniers groupes ne sont pas recopies a la main : ils sont
lus dans le resultat de la recherche verifiee, ou chaque reference a du etre
confirmee par son propre resume avant d'etre retenue.
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
import urllib.request

ICI = pathlib.Path(__file__).resolve().parent.parent
SORTIE = pathlib.Path(
    "fichier de travail transitoire, hors depot"
    r"C--Users-uriel-Documents--12-RUE-ANTOINE-CARLES--LYRICS/"
    r"dec6f719-0e04-49f9-9309-e1ada96e0b4c/tasks/w0eavjcoc.output")
NCBI = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        "?db=pubmed&retmode=json&id=")

DOSE = (
    u"On parle de «\u202fdose\u202f» comme si la relation entre ce qui est bu et ce "
    u"qui agit était proportionnelle. Elle ne l\u2019est pas, et c\u2019est la "
    u"propriété centrale de cette association.\n\n"
    u"<strong>Zéro plus un peu égale beaucoup.</strong> La DMT avalée seule ne "
    u"produit rien : la monoamine oxydase A la détruit intégralement au premier "
    u"passage. Les bêta-carbolines seules produisent peu. Ensemble, elles "
    u"produisent l\u2019effet complet. Ce n\u2019est pas une addition, c\u2019est "
    u"un seuil, et toute la pratique repose dessus.\n\n"
    u"<strong>L\u2019inhibition enzymatique n\u2019est pas proportionnelle non "
    u"plus.</strong> Le rapport entre le pourcentage d\u2019enzyme inhibée et "
    u"l\u2019exposition au substrat est hyperbolique : passer de 50 à 90\u202f% "
    u"d\u2019inhibition change modérément les choses, passer de 90 à 99\u202f% les "
    u"change beaucoup. Et lorsque l\u2019enzyme est saturée, la clairance cesse "
    u"d\u2019être d\u2019ordre un : un petit supplément de dose produit alors un "
    u"grand supplément de concentration. C\u2019est le domaine classique de la "
    u"cinétique non linéaire.\n\n"
    u"<strong>La même personne n\u2019a pas la même enzyme que son voisin.</strong> "
    u"L\u2019harmine est métabolisée par le cytochrome P450 2D6, dont le "
    u"polymorphisme est très étendu dans la population. Callaway a décrit en 2005, "
    u"chez quatorze membres expérimentés d\u2019une même église ayant reçu une dose "
    u"standardisée, deux sous-groupes : <em>métaboliseurs rapides et lents</em>. Le "
    u"détail compte : pour compenser cette variabilité, la quantité servie y est "
    u"décidée individuellement par le mestre, à vue. L\u2019institution qui pratique "
    u"le rite a donc identifié le problème et y répond par le jugement d\u2019une "
    u"personne, non par une mesure.\n\n"
    u"<strong>Et la dose elle-même n\u2019est pas connue.</strong> La teneur en "
    u"alcaloïdes varie d\u2019une préparation à l\u2019autre, et les travaux "
    u"analytiques sur la décoction le montrent, y compris sa stabilité dans le "
    u"temps. Il n\u2019y a ni titrage ni étiquette. On ne peut pas doser ce "
    u"qu\u2019on ne mesure pas.\n\n"
    u"<strong>Ce qu\u2019il faut en tirer, et c\u2019est contre-intuitif.</strong> "
    u"Un historique d\u2019expositions sans incident ne prédit pas la suivante. "
    u"L\u2019argument «\u202fil en avait déjà pris souvent sans problème\u202f» "
    u"suppose une relation dose-effet régulière ; dans un système à clairance "
    u"saturable, à inhibition hyperbolique et à teneur variable, cette régularité "
    u"n\u2019existe pas. C\u2019est aussi ce qui ruine la notion "
    u"d\u2019administration «\u202fmaîtrisée\u202f» ou «\u202fdosée\u202f» par un "
    u"tiers.\n\n"
    u"<strong>Une source de ce groupe va dans l\u2019autre sens, et elle y "
    u"reste.</strong> L\u2019évaluation du risque de Gable conclut à une marge de "
    u"sécurité comparable à la codéine ou à la méthadone, et à un potentiel de "
    u"dépendance minime. Elle précise cependant que des effets indésirables "
    u"peuvent survenir «\u202fparticulièrement lorsque des substances "
    u"sérotoninergiques sont utilisées conjointement\u202f» — ce qui est exactement "
    u"le sujet de ce groupe."
)

FND = (
    u"Ce groupe existe parce qu\u2019un raisonnement circule : les troubles "
    u"neurologiques fonctionnels seraient la passerelle entre une intoxication et "
    u"des symptômes durables sans lésion visible. La première moitié du "
    u"raisonnement est juste. La seconde ne l\u2019est pas, et mieux vaut le lire "
    u"ici.\n\n"
    u"<strong>Ce qui est solidement établi.</strong> Le trouble neurologique "
    u"fonctionnel n\u2019est ni une simulation, ni une maladie imaginaire, ni un "
    u"diagnostic d\u2019exclusion. Il se pose sur des <em>signes positifs</em> "
    u"d\u2019incompatibilité clinique. Le DSM-5 a supprimé l\u2019exigence d\u2019un "
    u"facteur de stress psychologique identifiable : un tel trouble peut donc être "
    u"retenu sans qu\u2019aucun conflit psychique ne soit démontré. Une revue de "
    u"<cite>Nature Reviews Neurology</cite> est consacrée à démonter point par "
    u"point l\u2019assimilation à la feinte. Et l\u2019objection «\u202fon a pu "
    u"passer à côté d\u2019une lésion\u202f» a sa réponse : le taux de révision "
    u"diagnostique est tombé autour de 4\u202f%, comparable à celui des autres "
    u"diagnostics neurologiques.\n\n"
    u"<strong>Un événement physique peut précipiter.</strong> Deux travaux "
    u"documentent le rôle d\u2019une blessure physique dans la survenue de symptômes "
    u"moteurs et sensitifs fonctionnels, et les facteurs précipitants physiques en "
    u"général. C\u2019est l\u2019analogue le plus proche d\u2019un déclenchement par "
    u"un événement aigu.\n\n"
    u"<strong>Et maintenant ce qui ne tient pas.</strong> AUCUN TRAVAIL INDEXÉ NE "
    u"RELIE UN TROUBLE NEUROLOGIQUE FONCTIONNEL À UNE INTOXICATION PAR "
    u"HALLUCINOGÈNE SÉROTONINERGIQUE. Pire pour qui voudrait l\u2019invoquer : à "
    u"cette intersection, toute la littérature indexée va en sens <em>inverse</em>, "
    u"et étudie les psychédéliques comme <em>traitement possible</em> du trouble "
    u"fonctionnel. Une revue systématique de 2025 des facteurs prédisposants, "
    u"précipitants et pérennisants ne retient aucun facteur toxique ni "
    u"médicamenteux parmi les précipitants. L\u2019absence est donc constatée par "
    u"une revue systématique récente, et pas seulement par un échec de recherche. "
    u"Le seul déclenchement pharmacologique publié est un cas isolé après propofol.\n\n"
    u"<strong>Deux précisions qui évitent une surinterprétation.</strong> Les "
    u"anomalies de volume et de connectivité décrites ici sont des résultats de "
    u"<em>groupe</em> : une IRM normale ne réfute pas le diagnostic, et une IRM "
    u"anormale ne le prouve pas chez une personne donnée. Et le trouble persistant "
    u"des perceptions après hallucinogène n\u2019est pas un trouble fonctionnel : "
    u"c\u2019est une entité distincte du DSM, et aucun travail n\u2019établit de "
    u"continuité entre les deux. Pour des séquelles visuelles après hallucinogène, "
    u"c\u2019est ce trouble-là qu\u2019il faut citer, et dire qu\u2019il n\u2019est "
    u"pas un trouble fonctionnel."
)

COUL = (
    u"La xanthopsie — voir jaune — est un signe classique, et l\u2019attribuer à "
    u"l\u2019ayahuasca est une tentation qu\u2019il faut traiter franchement.\n\n"
    u"<strong>Ce qui est établi.</strong> Les déficits <em>acquis</em> de la vision "
    u"des couleurs existent, se mesurent, et ont une sémiologie propre : l\u2019axe "
    u"bleu-jaune est le plus vulnérable, parce que les cônes S ne représentent "
    u"qu\u2019une faible proportion des cônes. La xanthopsie de l\u2019intoxication "
    u"digitalique est documentée jusqu\u2019au cas récent. Les atteintes "
    u"chromatiques d\u2019origine médicamenteuse sont répertoriées, celle de la "
    u"névrite optique est décrite, et la sérotonine est bien présente dans la "
    u"rétine.\n\n"
    u"<strong>Et voici le résultat négatif, qui a autant de valeur.</strong> IL "
    u"N\u2019EXISTE, DANS LA LITTÉRATURE INDEXÉE, AUCUN CAS PUBLIÉ DE XANTHOPSIE NI "
    u"DE DÉFICIT ACQUIS DE LA VISION DES COULEURS APRÈS AYAHUASCA, DMT OU "
    u"PSYCHÉDÉLIQUE SÉROTONINERGIQUE. Ni série, ni cas isolé, ni lettre. Les "
    u"requêtes croisant ayahuasca avec vision des couleurs, xanthopsie ou "
    u"dyschromatopsie renvoient zéro notice.\n\n"
    u"<strong>La distinction qui décide.</strong> Le trouble persistant des "
    u"perceptions après hallucinogène décrit bien une <em>intensification</em> des "
    u"couleurs, des images rémanentes, des traînées. Mais aucun de ces travaux ne "
    u"documente un déficit chromatique <em>mesuré</em> à l\u2019anomaloscope, au "
    u"Farnsworth-Munsell 100 Hue ou au test de Lanthony. Une plainte perceptive "
    u"n\u2019est pas une perte objectivée de discrimination des couleurs, et "
    u"confondre les deux devant un expert coûte cher.\n\n"
    u"<strong>Ce qu\u2019il ne faut pas transposer.</strong> Aucun travail "
    u"n\u2019attribue aux alcaloïdes harmala ni à la DMT une inhibition de la pompe "
    u"Na+/K+ ATPase rétinienne : ce mécanisme reste celui des glycosides "
    u"cardiotoniques. Le seul analogue publié plausible est une xanthopsie aiguë "
    u"sous rispéridone — une molécule qui <em>bloque</em> les récepteurs "
    u"sérotoninergiques, et non un agoniste 5-HT2A. Rien, à ce jour, sur un "
    u"agoniste.\n\n"
    u"La question est pourtant techniquement traitable : elle a été posée pour "
    u"d\u2019autres substances, par mesure calibrée avant et après administration. "
    u"Elle ne l\u2019a pas été pour l\u2019ayahuasca."
)

EXAM = (
    u"Voici les examens qui objectivent une plainte visuelle, avec ce que chacun "
    u"mesure — et, à la fin, ce que cette liste ne vaut pas.\n\n"
    u"<strong>La vision des couleurs.</strong> Les planches d\u2019Ishihara ne "
    u"dépistent que le déficit congénital rouge-vert : elles sont <em>inadaptées</em> "
    u"à un déficit acquis. Les planches Hardy-Rand-Rittler et les tests de rangement "
    u"sont complémentaires par construction — pseudo-isochromatiques pour le "
    u"dépistage, rangement pour l\u2019axe et la sévérité — et leurs limites "
    u"d\u2019emploi sont documentées.\n\n"
    u"<strong>La structure.</strong> La tomographie par cohérence optique mesure la "
    u"couche des fibres nerveuses et surtout le complexe cellules ganglionnaires "
    u"— couche plexiforme interne, dont l\u2019amincissement précède la baisse "
    u"d\u2019acuité.\n\n"
    u"<strong>La fonction.</strong> L\u2019électrophysiologie visuelle a ses normes "
    u"internationales, dont celle de l\u2019électrorétinogramme multifocal, et sa "
    u"place est établie dans l\u2019évaluation des atteintes toxiques. La périmétrie "
    u"cherche le scotome cæco-central des neuropathies optiques toxiques.\n\n"
    u"<strong>La pupille.</strong> Le diamètre pupillaire est une fenêtre sur "
    u"l\u2019activité du locus cœruleus et sur la charge cognitive.\n\n"
    u"<strong>Ce que cette liste ne vaut pas, et il faut le dire sur la même "
    u"page.</strong> AUCUNE DE CES EXPLORATIONS N\u2019A ÉTÉ APPLIQUÉE À DES "
    u"CONSOMMATEURS D\u2019AYAHUASCA DANS UN TRAVAIL INDEXÉ : ni série, ni mesure "
    u"OCT, ni potentiels évoqués, ni électrorétinogramme, ni pupillométrie. Toute "
    u"cette batterie est <em>transposée</em> d\u2019autres toxiques — éthambutol, "
    u"méthanol, tabac-alcool, hydroxychloroquine. Il n\u2019existe aucune "
    u"recommandation ni batterie validée pour la plainte visuelle post-toxique ; la "
    u"recommandation américaine sur l\u2019hydroxychloroquine sert de modèle de "
    u"l\u2019art, pas de norme applicable. Aucune donnée de sensibilité ou de "
    u"spécificité n\u2019existe pour quelque examen que ce soit dans un trouble "
    u"perceptif post-hallucinogène. Le scotome cæco-central garde une valeur "
    u"descriptive et classique, non chiffrée.\n\n"
    u"<strong>Et une mise en garde particulière.</strong> La littérature "
    u"pupille–charge cognitive–locus cœruleus est de la neuroscience cognitive : "
    u"sujets sains, tâches expérimentales, effets de groupe. Aucun seuil, aucune "
    u"valeur de référence exploitable sur un sujet unique, aucune validation "
    u"médico-légale. La pupillométrie dynamique est <em>exploratoire</em>, et la "
    u"présenter comme probante serait une surinterprétation."
)

TVO = (
    u"Avant de conclure qu\u2019un obscurcissement visuel transitoire est "
    u"fonctionnel, il faut écarter ce qui tue ou rend aveugle. C\u2019est une "
    u"question clinique avant d\u2019être une question de dossier.\n\n"
    u"<strong>Le symptôme est décrit de longue date</strong>, y compris — et "
    u"c\u2019est le point — <em>sans œdème papillaire</em>. Un fond d\u2019œil normal "
    u"ne suffit donc pas à écarter la cause.\n\n"
    u"<strong>L\u2019hypertension intracrânienne idiopathique.</strong> Son "
    u"diagnostic repose sur la <em>pression d\u2019ouverture mesurée</em>, et son "
    u"intervalle de référence est publié. L\u2019imagerie apporte des signes, dont "
    u"la valeur a été évaluée en méta-analyse, mais elle peut être prise en défaut. "
    u"Une recommandation européenne existe.\n\n"
    u"<strong>La piste vasculaire.</strong> Une cécité monoculaire transitoire "
    u"expose à un risque d\u2019accident vasculaire, et l\u2019origine vasculaire "
    u"des troubles visuels transitoires aigus a été étudiée pour elle-même.\n\n"
    u"<strong>Ce que la littérature ne donne pas.</strong> Aucune recommandation "
    u"française n\u2019est indexée : la page cite le référentiel européen et le dit. "
    u"Aucune étude ne donne la sensibilité, la spécificité ni la valeur prédictive "
    u"de l\u2019obscurcissement visuel transitoire pour une hypertension "
    u"intracrânienne ; aucune cohorte ne part d\u2019obscurcissements isolés à fond "
    u"d\u2019œil et imagerie normaux pour dire quelle proportion finit avec une "
    u"pression élevée.\n\n"
    u"<strong>Et le seuil lui-même est discuté</strong>, ce qui compte pour qui "
    u"voudrait faire reposer une conclusion sur une mesure unique : le travail le "
    u"plus récent confrontant la ponction lombaire à un monitorage continu conclut "
    u"que les deux ne sont pas interchangeables, la ponction surestimant "
    u"systématiquement et ne captant ni la variabilité posturale ni la variabilité "
    u"circadienne. Deux causes graves ne sont pas couvertes ici faute "
    u"d\u2019avoir été cherchées : l\u2019artérite à cellules géantes après "
    u"cinquante ans, et la thrombose veineuse cérébrale, qui n\u2019existe à ce "
    u"sujet qu\u2019à l\u2019état de cas isolés."
)

# Groupe 1 : ecrit a la main. Les quatre autres prennent leurs PMID
# dans le resultat de la recherche verifiee.
NOUVEAUX = [
    (u"La dose n\u2019est pas linéaire, et elle n\u2019est pas connue",
     u"Pharmacologie et mécanismes", DOSE,
     ["10404423",   # Callaway, pharmacocinetique du hoasca chez l'homme
      "16149329",   # Callaway, metaboliseurs rapides et lents
      "18454322",   # Yu, indolealkylamines, CYP2D6, interactions
      "12777961",   # Yu, le CYP2D6 et les substrats endogenes
      "2044328",    # Ludden, cinetique non lineaire : implications cliniques
      "35207420",   # Niznansky, la decoction appliquee a l'homme, analytique
      "31635364",   # Simao, determination des composants principaux
      "32365548",   # de Oliveira Silveira, stabilite de la DMT et des harmala
      "20942780",   # Shen, metabolisme du 5-MeO-DMT
      "26976063",   # Dominguez-Clave, pharmacologie et neurosciences
      "31523132",   # Scotton, syndrome serotoninergique : physiopathologie
      "17207120"],  # Gable, evaluation du risque (deja sur la page : dedoublonne)
     None),
    (u"Les troubles neurologiques fonctionnels : ce que le mot veut dire",
     u"Clinique et séquelles", FND, None, "fnd"),
    (u"La vision des couleurs : ce qui se mesure, et ce qui n\u2019a jamais été observé",
     u"Clinique et séquelles", COUL, None, "couleurs"),
    (u"Les examens neuro-ophtalmologiques, et ce qu\u2019ils ne prouvent pas",
     u"Ce que les examens trouvent", EXAM, None, "examens"),
    (u"Obscurcissements visuels : ce qu\u2019il faut écarter d\u2019abord",
     u"Ce que les examens trouvent", TVO, None, "drapeaux"),
]

DOUTEUX = ("correction to", "erratum", "corrigendum", "retraction",
           "author correction", "expression of concern")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    rech = json.loads(SORTIE.read_text(encoding="utf-8", errors="replace"))["result"]
    par_cle = dict((d["cle"], d) for d in rech)
    cats = set(g.get("cat") for g in gr)

    for titre, cat, intro, pmids, cle in NOUVEAUX:
        if any(g["titre"] == titre for g in gr):
            print(u"déjà présent, ignoré : %s" % titre)
            continue
        if cat not in cats:
            sys.exit(u"catégorie inconnue : %s" % cat)
        if pmids is None:
            pmids = [r["pmid"] for r in par_cle[cle]["retenues"]]

        deja = set(r["pmid"] for g in gr for r in g["refs"])
        ou = dict((r["pmid"], g["titre"]) for g in gr for r in g["refs"])
        neufs = [p for p in pmids if p not in deja]
        for p in pmids:
            if p in deja:
                print(u"    dédoublonné : %s déjà dans « %s »" % (p, ou[p][:40]))
        if not neufs:
            print(u"  rien de neuf pour : %s" % titre)
            continue

        with urllib.request.urlopen(NCBI + ",".join(neufs), timeout=120) as r:
            res = json.loads(r.read().decode("utf-8"))["result"]
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
                print(u"    ECARTE (sans auteur, sans revue, ou erratum) : %s  %s"
                      % (p, t[:42]))
                continue
            refs.append({"pmid": p, "auteur": a[0]["name"], "nb": len(a),
                         "revue": rev, "annee": (e.get("pubdate") or "")[:4],
                         "t": t})
        # Chaque groupe se range a la fin de sa categorie.
        dernier = max(i for i, g in enumerate(gr) if g.get("cat") == cat)
        gr.insert(dernier + 1,
                  {"titre": titre, "cat": cat, "intro": intro, "refs": refs})
        print(u"  ajouté : %-58s %2d notices" % (titre[:58], len(refs)))

    with io.open(str(ICI / "page_data.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        f.write(json.dumps(gr, ensure_ascii=False, indent=1) + "\n")

    print(u"\n%d groupes, %d notices PubMed" % (len(gr), sum(len(g["refs"]) for g in gr)))
    vus, casse = [], []
    for g in gr:
        c = g.get("cat")
        if not vus or vus[-1] != c:
            if c in vus:
                casse.append(c)
            vus.append(c)
    print(u"  ordre des catégories : %s"
          % (u"intact" if not casse else u"ENTRELACE : %s" % casse))
    for c in vus:
        n = [g for g in gr if g.get("cat") == c]
        print(u"    %-38s %2d groupes  %3d notices"
              % (c, len(n), sum(len(g["refs"]) for g in n)))


if __name__ == "__main__":
    main()
