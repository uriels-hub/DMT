# -*- coding: utf-8 -*-
"""Ajoute ce qui etait valide dans le rapport v2 mais absent de la page.

Cinq notices PubMed et quatre sources juridiques. L'audit avait montre que
15 des 20 references validees y figuraient, et que le volet juridique de
l'imputabilite n'y figurait pas du tout.

Les metadonnees PubMed ne sont pas ecrites ici : elles sont telechargees.
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

# PMID -> debut du titre du groupe d'accueil.
PLACEMENT = [
    ("25713771", u"Le mythe du révélateur"),      # Szmulewicz : le cas index
    ("37810598", u"Le mythe du révélateur"),      # Halim : manie apres psilocybine
    ("39564729", u"Toxicité, événements"),        # Yildirim : revue des effets indesirables
    ("20126400", u"La DMT est-elle un dissociatif"),   # Ray : le receptorome
    ("27216487", u"La DMT est-elle un dissociatif"),   # Rickli : profils de liaison
]

JURIDIQUE = [
    {
        "grp": u"Droit français",
        "id": u"Cass. 2e civ., 20 mai 2020, n° 18-24.095",
        "u": "https://www.legifrance.gouv.fr/juri/id/JURITEXT000041995744/",
        "t": (u"Publié au Bulletin. Le droit à indemnisation ne peut être réduit "
              u"pour une prédisposition pathologique lorsque l’affection n’a été "
              u"provoquée ou révélée que du fait de l’accident. En l’espèce une "
              u"maladie de Parkinson, absente avant l’accident et jugée révélée "
              u"par lui : réparation intégrale."),
        "a": u"2e chambre civile, arrêt n° 417, ECLI:FR:CCASS:2020:C200417",
        "s": u"Cour de cassation, rejet du pourvoi contre CA Bordeaux, 3 septembre 2018",
        "y": u"2020",
    },
    {
        "grp": u"Droit français",
        "id": u"Cass. 2e civ., 9 février 2023, n° 21-12.657",
        "u": "https://www.legifrance.gouv.fr/juri/id/JURITEXT000047200927",
        "t": (u"Même principe, confirmé en 2023 : « le droit de la victime ne "
              u"saurait être réduit en raison d’une prédisposition pathologique "
              u"lorsque l’affection qui en est résultée n’a été provoquée ou "
              u"révélée que du fait de l’accident ». Décision inédite au Bulletin, "
              u"à citer en appui de l’arrêt publié de 2020 et non à sa place."),
        "a": u"2e chambre civile, ECLI:FR:CCASS:2023:C200150",
        "s": u"Cour de cassation, cassation partielle, CA Aix-en-Provence, 7 janvier 2021",
        "y": u"2023",
    },
    {
        "grp": u"Droit français",
        "id": u"CSP, art. R4127-35",
        "u": ("https://www.conseil-national.medecin.fr/code-deontologie/"
              "devoirs-patients-art-32-55/article-35-information-patient"),
        "t": (u"Devoir d’information : le médecin doit une information loyale, "
              u"claire et appropriée sur l’état, les investigations et les soins "
              u"proposés. En cas de litige, c’est au professionnel de prouver "
              u"que l’information a été donnée."),
        "a": u"Code de déontologie médicale, article 35",
        "s": u"Conseil national de l’Ordre des médecins",
        "y": u"en vigueur",
    },
    {
        "grp": u"Droit français",
        "id": u"CSP, art. R4127-32",
        "u": ("https://www.conseil-national.medecin.fr/code-deontologie/"
              "devoirs-patients-art-32-55/article-32-qualite-soins"),
        "t": (u"Qualité des soins : le médecin s’engage à donner des soins "
              u"consciencieux, dévoués et fondés sur les données acquises de la "
              u"science."),
        "a": u"Code de déontologie médicale, article 32",
        "s": u"Conseil national de l’Ordre des médecins",
        "y": u"en vigueur",
    },
]

DOUTEUX = ("correction to", "erratum", "corrigendum", "retraction",
           "author correction", "expression of concern")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    au = json.loads((ICI / "page_autres.json").read_text(encoding="utf-8"))

    deja = set(r["pmid"] for g in gr for r in g["refs"])
    neufs = [p for p, _ in PLACEMENT if p not in deja]
    for p, _ in PLACEMENT:
        if p in deja:
            print(u"  deja present, ignore : %s" % p)

    if neufs:
        with urllib.request.urlopen(NCBI + ",".join(neufs), timeout=120) as r:
            res = json.loads(r.read().decode("utf-8"))["result"]
        for pmid, cible in PLACEMENT:
            if pmid not in neufs:
                continue
            e = res.get(pmid)
            if not e:
                print(u"  INTROUVABLE : %s" % pmid)
                continue
            a = e.get("authors") or []
            t = e.get("title", "").rstrip(".")
            if not a or any(m in t.lower() for m in DOUTEUX):
                print(u"  CE N'EST PAS UNE SOURCE : %s" % pmid)
                continue
            hotes = [g for g in gr if g["titre"].startswith(cible)]
            if not hotes:
                print(u"  GROUPE D'ACCUEIL INTROUVABLE : %s (pour %s)" % (cible, pmid))
                continue
            hotes[0]["refs"].append({
                "pmid": pmid, "auteur": a[0]["name"], "nb": len(a),
                "revue": e.get("source", ""), "annee": (e.get("pubdate") or "")[:4],
                "t": t,
            })
            print(u"  %-9s -> %-34s  %s"
                  % (pmid, hotes[0]["titre"][:34], t[:44]))

    ids = set(a["id"] for a in au)
    for j in JURIDIQUE:
        if j["id"] in ids:
            print(u"  deja present : %s" % j["id"])
            continue
        au.append(j)
        print(u"  juridique ajoute : %s" % j["id"])

    # Les sources hors PubMed sont rendues dans l'ordre du fichier : on
    # regroupe les nouvelles avec les autres entrees de leur rubrique.
    ordre = list(dict.fromkeys(a["grp"] for a in au))
    au.sort(key=lambda a: ordre.index(a["grp"]))

    for nom, obj in (("page_data.json", gr), ("page_autres.json", au)):
        with io.open(str(ICI / nom), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")
    print(u"\n%d notices PubMed, %d hors PubMed, %d au total"
          % (sum(len(g["refs"]) for g in gr), len(au),
             sum(len(g["refs"]) for g in gr) + len(au)))


if __name__ == "__main__":
    main()
