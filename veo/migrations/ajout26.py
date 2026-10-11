# -*- coding: utf-8 -*-
"""Ajoute le groupe sur la consommation répétée et les dérèglements mesurés.

Le groupe tient sur une distinction qu'il faut garder nette :

  mesuré chez l'homme   les effets autonomiques, neuroendocriniens et
                        immunologiques de doses répétées
  mesuré en laboratoire l'allongement de la période circadienne par l'harmine
  établi comme classe   l'agonisme 5-HT2B fibrose les valves cardiaques, et
                        trois médicaments ont été retirés pour cela
  NON démontré          aucune échocardiographie publiée chez des usagers

La dernière ligne est la plus importante. Le mécanisme justifie de demander
l'examen ; il ne permet pas d'en préjuger le résultat.
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

TITRE = u"La consommation répétée : ce qui se dérègle, et l\u2019inquiétude valvulaire"

INTRO = (
    u"La question de l\u2019usage chronique se pose mal si l\u2019on cherche "
    u"«\u202fune\u202f» lésion. Ce qui est documenté, c\u2019est une série de "
    u"dérèglements mesurés, et une inquiétude de classe qui ne concerne que le "
    u"dosage répété.\n\n"
    u"<strong>Ce qui est mesuré chez l\u2019homme.</strong> L\u2019équipe de "
    u"Rafael Dos Santos a publié les effets autonomiques, neuroendocriniens et "
    u"immunologiques de l\u2019ayahuasca, puis la pharmacologie de deux doses "
    u"rapprochées, puis les effets immunologiques seuls. Ce ne sont pas des "
    u"hypothèses : ce sont des paramètres relevés, qui bougent. Strassman avait "
    u"établi dès 1996 que la tolérance est <em>différentielle</em> — le corps "
    u"s\u2019habitue, l\u2019expérience non — point traité en détail au groupe sur "
    u"l\u2019accoutumance.\n\n"
    u"<strong>L\u2019horloge biologique, elle, se dérègle de façon "
    u"démontrable.</strong> L\u2019harmine allonge la période circadienne de "
    u"l\u2019horloge moléculaire dans le noyau suprachiasmatique, en augmentant la "
    u"stabilité de la protéine PER2. C\u2019est du laboratoire, pas de la clinique, "
    u"mais c\u2019est un alcaloïde de la décoction agissant sur l\u2019horloge "
    u"centrale elle-même.\n\n"
    u"<strong>L\u2019inquiétude valvulaire est la plus sérieuse, et elle est mal "
    u"connue.</strong> L\u2019agonisme du récepteur 5-HT2B fibrose les feuillets "
    u"des valves cardiaques. Ce n\u2019est pas une théorie : les fenfluramines ont "
    u"été retirées du marché américain en 1997 et le pergolide en 2007 pour cette "
    u"raison, et la France connaît le dossier sous le nom de benfluorex, pour les "
    u"valves et l\u2019hypertension pulmonaire. La revue de référence sur les "
    u"valvulopathies médicamenteuses attribue le mécanisme à un effet "
    u"«\u202fhors cible\u202f» sur le 5-HT2B exprimé sur les valves — et précise "
    u"deux choses décisives : ces effets <em>n\u2019avaient pas été prédits</em> "
    u"par les études de toxicité de routine, et il n\u2019existe toujours pas de "
    u"criblage préclinique validé pour les prédire.\n\n"
    u"Or les psychédéliques se lient bel et bien à ce récepteur : la structure "
    u"cristalline du LSD a été résolue sur le 5-HT2B lui-même, publiée dans "
    u"<em>Cell</em> en 2017. Et le champ traite ce risque comme actuel, pas "
    u"historique : un travail de 2025 propose une cothérapie pour "
    u"«\u202fatténuer les préoccupations de sécurité liées au 5-HT2B\u202f» et "
    u"améliorer la sécurité cardiaque de la psilocybine, et une revue de 2026 "
    u"construit un cadre de décision cardiovasculaire en notant que les "
    u"participants aux essais sont médicalement sélectionnés et surveillés bien "
    u"plus étroitement que les usagers ordinaires.\n\n"
    u"<strong>La limite, et elle compte autant que le reste.</strong> AUCUNE "
    u"ÉTUDE ÉCHOCARDIOGRAPHIQUE N\u2019A MONTRÉ DE VALVULOPATHIE CHEZ DES USAGERS "
    u"DE PSYCHÉDÉLIQUES. C\u2019est une inquiétude mécaniquement fondée et "
    u"explicitement publiée par les pharmacologues du domaine, ce n\u2019est pas un "
    u"résultat démontré. La conséquence pratique est simple et ne va pas plus "
    u"loin que les sources : une échocardiographie est un examen courant et peu "
    u"coûteux, le mécanisme justifie de la demander devant un usage répété, et "
    u"elle trancherait dans un sens comme dans l\u2019autre. Demander l\u2019examen "
    u"n\u2019est pas préjuger du résultat."
)

PMIDS = [
    # Ce qui est mesure chez l'homme, doses repetees
    "22005052",   # Dos Santos, effets autonomiques, neuroendocriniens, immunologiques
    "21842159",   # Dos Santos, pharmacologie de deux doses rapprochees
    "25364989",   # Dos Santos, effets immunologiques chez l'homme
    "27918874",   # Dos Santos, effets de l'harmine, beta-carboline naturelle
    "8788488",    # Strassman, psychopharmacologie humaine de la DMT
    # L'horloge circadienne
    "25087965",   # Kondoh, l'harmine allonge la periode circadienne dans le NSC
    # L'affinite pour le 5-HT2B : ce qui rend l'inquietude legitime
    "28129538",   # Wacker, Cell : structure cristalline du LSD lie au 5-HT2B
    "26739781",   # Cozzi, profils de liaison des tryptamines
    "30261175",   # Eshleman, pharmacologie des tryptamines substituees
    # La valvulopathie comme effet de classe
    "20716786",   # Elangbam, valvulopathies medicamenteuses : la revue de reference
    "24817577",   # Szymanski, benfluorex : valves et hypertension pulmonaire
    "33895186",   # Odi, la fenfluramine, du poids a l'epilepsie
    # La securite cardiovasculaire des psychedeliques, telle que le champ la pose
    "42538465",   # Szarpak, securite cardiovasculaire de la psilocybine
    "41256989",   # Renner, atenuer les risques lies au 5-HT2B
    "36884348",   # Lewis, un analogue non hallucinogene du LSD
    "22580238",   # Dawson, toxicite cardiovasculaire des nouveaux produits
    # Le dosage repete comme pratique
    "40105807",   # Mueller, JAMA Psychiatry : LSD a faible dose repetee
    "32922736",   # Kuypers, potentiel therapeutique du microdosage
    "30604183",   # Anderson, microdosage : personnalite et sante mentale
    "17207120",   # Gable, evaluation du risque de l'usage rituel de DMT orale
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
            print(u"  déjà sur la page, retiré : %s  [%s]" % (p, ou[p][:46]))

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
            "pmid": p, "auteur": a[0]["name"], "nb": len(a),
            "revue": e.get("source", ""), "annee": (e.get("pubdate") or "")[:4],
            "t": t,
        })

    # L'intro renvoie au groupe sur l'accoutumance : il doit exister.
    cible = [g["titre"] for g in gr if g["titre"].startswith(u"Accoutumance")]
    print(u"\nrenvoi vers le groupe accoutumance : %s"
          % (cible[0] if cible else u"INTROUVABLE — corriger l'intro"))

    gr.append({"titre": TITRE, "intro": INTRO, "refs": refs})
    with io.open(str(ICI / "page_data.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        f.write(json.dumps(gr, ensure_ascii=False, indent=1) + "\n")
    print(u"\najouté : %s\n  %d notices" % (TITRE, len(refs)))
    for r in refs:
        print(u"    %-9s %-5s %-24s %s"
              % (r["pmid"], r["annee"], r["revue"][:24], r["t"][:48]))
    print(u"\n%d groupes, %d notices PubMed au total"
          % (len(gr), sum(len(g["refs"]) for g in gr)))


if __name__ == "__main__":
    main()
