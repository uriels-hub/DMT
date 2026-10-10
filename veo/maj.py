#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Actualise tous les livrables documentaires de TOXICOSQUEROS.

    .venv/Scripts/python.exe maj.py            # tout
    .venv/Scripts/python.exe maj.py notices    # recharge les notices PubMed seulement
    .venv/Scripts/python.exe maj.py page       # regenere la page publique
    .venv/Scripts/python.exe maj.py srt        # regenere les sous-titres
    .venv/Scripts/python.exe maj.py liens      # ouvre chaque lien de la page

Chaque execution verifie en fin de course les fins de ligne des livrables :
CRLF pour les .srt (norme SubRip), LF partout ailleurs.

Principe : aucun contenu bibliographique n'est redige. Les metadonnees viennent de
l'API NCBI E-utilities, le reste est assemble par gabarit. Une erreur possible est
une erreur de programme, pas une invention.

Fichiers de donnees, modifiables sans toucher au code :
    page_data.json     groupes thematiques et PMID
    page_autres.json   sources hors PubMed (identifiant stable + lien)
    prompts.json       paroles francaises, pour les sous-titres
    xx.json            une traduction par langue

Sorties :
    references_toxicosqueros.html   page publique
    ../TOXICOSQUEROS.<langue>.srt   sous-titres
"""
import io
import json
import pathlib
import re
import subprocess
import sys
import urllib.request

ICI = pathlib.Path(__file__).resolve().parent
NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id="


def lire(nom):
    return json.loads((ICI / nom).read_text(encoding="utf-8"))


def ecrire(nom, obj):
    # LF explicite : ce sont des donnees versionnables, pas des fichiers Windows.
    with io.open(str(ICI / nom), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")


# Fins de ligne voulues, par extension. Deux conventions, chacune pour une raison :
# .srt  CRLF  la norme SubRip, et les lecteurs les plus stricts n'acceptent que ca
# le reste LF  donnees et fichiers web, relus ailleurs que sous Windows
FINS = {".srt": "\r\n", ".html": "\n", ".json": "\n", ".md": "\n"}


def fins():
    """Verifie que chaque livrable porte la fin de ligne voulue, et rien d'autre."""
    cibles = sorted(ICI.parent.glob("TOXICOSQUEROS.*.srt"))
    cibles += [ICI.parent / "youtube_TOXICOSQUEROS.md",
               ICI / "references_toxicosqueros.html",
               ICI / "page_data.json", ICI / "page_autres.json"]
    ecarts = []
    for f in cibles:
        if not f.exists():
            continue
        b = f.read_bytes()
        crlf = b.count(b"\r\n")
        lf = b.count(b"\n") - crlf
        cr = b.count(b"\r") - crlf          # CR isole : vieux Mac, toujours une erreur
        voulu = FINS[f.suffix]
        melange = (crlf and lf) or cr
        faux = (voulu == "\r\n" and lf) or (voulu == "\n" and crlf)
        if melange or faux:
            ecarts.append((f.name, voulu, crlf, lf, cr))
        if f.suffix == ".srt" and not b.endswith(b"\r\n\r\n"):
            ecarts.append((f.name, "ligne vide finale", crlf, lf, cr))
    if ecarts:
        print("  FINS DE LIGNE a corriger :")
        for n, v, a, b_, c in ecarts:
            print("    %-28s attendu %-18r  CRLF %d  LF %d  CR %d"
                  % (n, v, a, b_, c))
    else:
        print("fins de ligne : %d fichiers conformes (SRT en CRLF, le reste en LF)"
              % len([f for f in cibles if f.exists()]))
    return not ecarts



# Un 403 n'est presque jamais un lien mort : c'est un filtre anti-robot.
# Legifrance en renvoie des qu'on enchaine les requetes, JAMA en renvoie
# toujours. On les signale a verifier a la main plutot que de crier au mort.
AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")


def liens():
    """Ouvre chaque URL de page_autres.json et rapporte ce qui repond."""
    import urllib.error
    autres = lire("page_autres.json")
    avec = [a for a in autres if a.get("u")]
    sans = [a for a in autres if not a.get("u")]
    print("%d sources hors PubMed : %d avec lien, %d sans"
          % (len(autres), len(avec), len(sans)))

    morts, douteux = [], []
    for a in avec:
        req = urllib.request.Request(a["u"], headers={"User-Agent": AGENT})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:
            code = str(e)[:40]
        if code == 200:
            continue
        (douteux if code in (403, 429) else morts).append((a["id"], code, a["u"]))

    if morts:
        print("  LIENS MORTS :")
        for i, c, u in morts:
            print("    %-34s %s  %s" % (i[:34], c, u[:70]))
    if douteux:
        print("  a verifier a la main (filtre anti-robot probable) :")
        for i, c, u in douteux:
            print("    %-34s %s  %s" % (i[:34], c, u[:70]))
    if sans:
        print("  sans lien, affichees avec leur seul identifiant :")
        for a in sans:
            print("    %s" % a["id"][:60])
    if not morts and not douteux:
        print("  les %d liens repondent." % len(avec))
    return not morts


def notices():
    """Recharge chaque notice depuis PubMed et signale toute divergence."""
    groupes = lire("page_data.json")
    pmids = [r["pmid"] for g in groupes for r in g["refs"]]
    print("Interrogation de PubMed : %d notices" % len(pmids))
    with urllib.request.urlopen(NCBI + ",".join(pmids), timeout=120) as r:
        res = json.loads(r.read().decode("utf-8"))["result"]

    absents, changes = [], []
    for g in groupes:
        for ref in g["refs"]:
            e = res.get(ref["pmid"])
            if not e:
                absents.append(ref["pmid"])
                continue
            au = e.get("authors") or []
            neuf = {
                "pmid": ref["pmid"],
                "auteur": au[0]["name"] if au else "?",
                "nb": len(au),
                "revue": e.get("source", ""),
                "annee": (e.get("pubdate", "") or "")[:4],
                "t": e.get("title", "").rstrip("."),
            }
            # "t" reste la verite PubMed ; "t_affiche" est un libelle choisi, jamais ecrase.
            for champ in ("auteur", "revue", "annee", "t"):
                if str(ref.get(champ, "")) != str(neuf[champ]):
                    changes.append((ref["pmid"], champ, ref.get(champ), neuf[champ]))
            ref.update(neuf)

    ecrire("page_data.json", groupes)

    # Deux defauts qui se reintroduisent a chaque ajout, et qui ne se voient
    # qu'a la lecture de la page : un jeton de formatage reste dans un libelle,
    # et une meme etude inscrite deux fois, une fois par son PMID et une fois
    # par son DOI. Le second est arrive deux fois.
    import difflib
    def _n(x):
        return re.sub(u"[^a-z0-9]", u"", (x or u"").lower())[:70]
    sales = [(gr["titre"][:34], c) for gr in groupes for c in ("titre", "intro")
             if "%%" in gr.get(c, "") or re.search(r"@[A-Z]{2,8}@", gr.get(c, ""))]
    if sales:
        print("  JETONS DE FORMATAGE restes dans un libelle :")
        for t, c in sales:
            print("    [%s] %s" % (t, c))
    autres = lire("page_autres.json")
    pm = [(r["pmid"], r.get("t", ""), gr["titre"]) for gr in groupes for r in gr["refs"]]
    doubles = []
    for x in autres:
        nx = _n(x.get("t"))
        if len(nx) < 25:
            continue
        for pmid, t, grp in pm:
            if difflib.SequenceMatcher(None, nx, _n(t)).ratio() > 0.88:
                doubles.append((x["id"], pmid, grp))
    if doubles:
        print("  MEME ETUDE DEUX FOIS, en hors PubMed et en notice PubMed :")
        for ident, pmid, grp in doubles:
            print("    %-34s = PMID %s  [%s]" % (ident[:34], pmid, grp[:30]))
    if not sales and not doubles:
        print("  aucun jeton reste, aucune etude en double.")


    # Un erratum n'est pas une source. PubMed les indexe comme des notices a part
    # entiere, sans auteur, et ils passent inapercus : « Correction to: ... » au
    # milieu de quatre-vingts references vraies, c'est la ligne qu'un lecteur
    # hostile releve. Meme chose pour les commentaires et les retractations.
    DOUTEUX = ("correction to", "erratum", "corrigendum", "retraction",
               "author correction", "expression of concern")
    suspects = [(r["pmid"], r["t"]) for gr in groupes for r in gr["refs"]
                if r.get("auteur") in ("?", "")
                or any(m in (r.get("t") or "").lower() for m in DOUTEUX)]
    if suspects:
        print("  A RETIRER, ce ne sont pas des sources :")
        for pm, t in suspects:
            print("    %s  %s" % (pm, t[:66]))

    if absents:
        print("  INTROUVABLES sur PubMed : %s" % ", ".join(absents))
    if changes:
        print("  %d divergences corrigees :" % len(changes))
        for p, c, a, b in changes:
            print("    %s %s : %r -> %r" % (p, c, a, b))
    if not absents and not changes:
        print("  Aucune divergence. Les %d notices sont inchangees." % len(pmids))
    return not absents


def page():
    subprocess.run([sys.executable, str(ICI / "page.py")], check=True, cwd=ICI)


def srt():
    subprocess.run([sys.executable, str(ICI / "srt.py")], check=True, cwd=ICI)


def etat():
    groupes = lire("page_data.json")
    autres = lire("page_autres.json")
    n = sum(len(g["refs"]) for g in groupes)
    print("\n%d references PubMed dans %d groupes, %d sources hors PubMed, %d au total"
          % (n, len(groupes), len(autres), n + len(autres)))
    srts = sorted((ICI.parent).glob("TOXICOSQUEROS.*.srt"))
    print("%d fichiers de sous-titres : %s"
          % (len(srts), ", ".join(p.name.split(".")[1] for p in srts)))
    html = ICI / "references_toxicosqueros.html"
    if html.exists():
        print("page : %d caracteres" % len(html.read_text(encoding="utf-8")))
    fins()
    print("\nPublier la page : Artifact sur references_toxicosqueros.html, "
          "en passant l'URL de l'artefact existant pour le mettre a jour.")


ETAPES = {"notices": notices, "liens": liens, "page": page, "srt": srt}

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    demande = sys.argv[1:] or ["notices", "page", "srt"]
    inconnues = [d for d in demande if d not in ETAPES]
    if inconnues:
        sys.exit("etape inconnue : %s (attendu : %s)"
                 % (", ".join(inconnues), ", ".join(ETAPES)))
    for d in demande:
        print("\n== %s" % d)
        ETAPES[d]()
    etat()
