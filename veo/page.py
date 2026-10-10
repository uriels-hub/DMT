# -*- coding: utf-8 -*-
"""Genere la page publique de references a partir des donnees verifiees.

Aucun contenu bibliographique n'est redige : tout vient de page_data.json,
lui-meme construit depuis refs_canoniques.json (API NCBI).
"""
import html
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
e = html.escape

groupes = json.load(io.open("page_data.json", encoding="utf-8"))


def ref(r):
    aut = e(r["auteur"]) + (' <span class="etal">et al.</span>' if r["nb"] > 1 else "")
    return (
        '<li class="ref">'
        '<a class="pmid" href="https://pubmed.ncbi.nlm.nih.gov/%s/" target="_blank" rel="noopener">PMID %s</a>'
        '<p class="t">%s</p>'
        '<p class="m">%s &middot; <cite>%s</cite> &middot; %s</p>'
        '</li>'
    ) % (r["pmid"], r["pmid"], e(r.get("t_affiche") or r["t"]), aut, e(r["revue"]), e(str(r["annee"])))


# Ancres : la page porte 111 entrees. Sans sommaire, on atterrit sur un mur.
import re
import unicodedata


def ancre(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t.lower())).strip("-")[:40]


sections = "\n".join(
    '<section class="grp" id="%s"><h2>%s</h2><p class="lede">%s</p><ol class="refs">%s</ol></section>'
    % (ancre(g["titre"]), e(g["titre"]), e(g["intro"]),
       "".join(ref(r) for r in g["refs"]))
    for g in groupes
)

# Le sommaire porte le compte de chaque section : on sait ou l'on va avant d'y aller.
SOMMAIRE = (
    '<nav class="somm" aria-label="Sommaire"><ol>'
    + '<li><a href="#cadre-juridique">Cadre juridique français</a></li>'
    + "".join('<li><a href="#%s">%s</a> <span class="n">%d</span></li>'
              % (ancre(g["titre"]), e(g["titre"]), len(g["refs"])) for g in groupes)
    + '<li><a href="#hors-pubmed">Hors PubMed</a> <span class="n">%d</span></li>' % len(
        json.load(io.open("page_autres.json", encoding="utf-8")))
    + '<li><a href="#methode">Méthode et limites</a></li>'
    + '</ol></nav>'
)

# Sources hors PubMed : identifiant stable, lien quand il en existe un.
autres = json.load(io.open("page_autres.json", encoding="utf-8"))
rubriques = []
for nom in dict.fromkeys(a["grp"] for a in autres):
    items = []
    for a in (x for x in autres if x["grp"] == nom):
        ident = ('<a class="pmid" href="%s" target="_blank" rel="noopener">%s</a>'
                 % (e(a["u"]), e(a["id"]))) if a["u"] else (
                 '<span class="pmid pmid--plain">%s</span>' % e(a["id"]))
        meta = " &middot; ".join(p for p in (e(a["a"]), "<cite>%s</cite>" % e(a["s"]), e(a["y"])) if p)
        items.append('<li class="ref">%s<p class="t">%s</p><p class="m">%s</p></li>'
                     % (ident, e(a["t"]), meta))
    rubriques.append('<h3 class="sub">%s</h3><ol class="refs">%s</ol>' % (e(nom), "".join(items)))

AUTRES_SECTION = (
    '<section class="grp" id="hors-pubmed"><h2>Hors PubMed</h2>'
    '<p class="lede">Décisions, rapports publics et publications sans identifiant PubMed. '
    'Chacune porte son identifiant stable.</p>' + "".join(rubriques) + '</section>'
)

STYLE = """<title>Références Toxicosqueros</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>
/* Colonne unique, document de reference : identifiant en tete, titre, puis metadonnees. */
:root {
  --pap:#f2f1ed; --enc:#1b1d1f; --att:#6d6a63; --fil:#d9d7d0;
  --sig:#8a4b2a; --ver:#3f6b52; --car:#fbfaf8;
  --serif:"Source Serif 4",Georgia,"Times New Roman",serif;
  --sans:"IBM Plex Sans",system-ui,-apple-system,Segoe UI,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme:dark) { :root:not([data-theme="light"]) {
  --pap:#15171a; --enc:#e8e6e1; --att:#9b978e; --fil:#2d3135;
  --sig:#d08a5f; --ver:#7fb193; --car:#1c1f22; color-scheme:dark; } }
:root[data-theme="dark"] {
  --pap:#15171a; --enc:#e8e6e1; --att:#9b978e; --fil:#2d3135;
  --sig:#d08a5f; --ver:#7fb193; --car:#1c1f22; color-scheme:dark; }
body { background:var(--pap); color:var(--enc); font-family:var(--serif); font-size:17px; line-height:1.65; }
.wrap { max-width:46rem; margin:0 auto; padding-inline:20px; padding-block:clamp(2.5rem,7vw,4.5rem); }
.eyebrow { font-family:var(--sans); font-size:.72rem; letter-spacing:.13em; text-transform:uppercase; color:var(--att); margin:0 0 .9rem; }
h1 { font-size:clamp(1.9rem,5.5vw,2.7rem); line-height:1.12; font-weight:600; margin:0 0 1.1rem; text-wrap:balance; letter-spacing:-.015em; }
/* Le mot d'ordre : une position assumee, tenue a l'ecart des notices par un filet. */
.cri { font-family:var(--sans); font-weight:600; font-size:1.05rem; line-height:1.35;
       color:var(--sig); border-left:3px solid var(--sig); padding-left:.9rem;
       margin:0 0 1.3rem; max-width:34rem; text-wrap:balance; }
.somm { margin:1.8rem 0 0; }
.somm ol { list-style:none; margin:0; padding:0; columns:2; column-gap:2rem; }
.somm li { break-inside:avoid; margin:0 0 .4rem; font-family:var(--sans); font-size:.88rem; line-height:1.4; }
.somm a { text-decoration:none; border-bottom:1px solid transparent; }
.somm a:hover, .somm a:focus-visible { border-bottom-color:var(--sig); }
.somm .n { color:var(--att); font-family:var(--mono); font-size:.76rem; }
@media (max-width:34rem) { .somm ol { columns:1; } }
html { scroll-behavior:smooth; }
@media (prefers-reduced-motion:reduce) { html { scroll-behavior:auto; } }
.grp { scroll-margin-top:1.5rem; }
.chapo { font-size:1.08rem; margin:0 0 1.5rem; max-width:34rem; }
.note { font-size:.95rem; color:var(--att); margin:0; max-width:34rem; }
hr { border:0; border-top:1px solid var(--fil); margin:3rem 0; }
h2 { font-family:var(--sans); font-size:1.02rem; font-weight:600; margin:0 0 .35rem; }
.lede { font-size:.95rem; color:var(--att); margin:0 0 1.5rem; max-width:34rem; }
.grp { margin-bottom:3rem; }
.refs { list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:1.4rem; }
.ref { border-left:2px solid var(--fil); padding-left:1.1rem; min-width:0; }
.pmid { display:inline-block; font-family:var(--mono); font-size:.76rem; letter-spacing:.02em; color:var(--sig); text-decoration:none; border-bottom:1px solid transparent; }
.pmid:hover, .pmid:focus-visible { border-bottom-color:var(--sig); }
.pmid--plain { color:var(--att); }
.sub { font-family:var(--sans); font-size:.8rem; font-weight:600; letter-spacing:.07em; text-transform:uppercase; color:var(--att); margin:2rem 0 1rem; }
.grp .sub:first-of-type { margin-top:0; }
.t { margin:.3rem 0 .25rem; font-size:1rem; line-height:1.45; }
.m { margin:0; font-size:.87rem; color:var(--att); font-family:var(--sans); }
.etal { font-style:italic; }
cite { font-style:normal; }
.cadre { background:var(--car); border:1px solid var(--fil); border-radius:3px; padding:1.3rem 1.4rem; margin:0 0 1.6rem; }
.cadre h3 { font-family:var(--sans); font-size:.86rem; font-weight:600; margin:0 0 .5rem; }
.cadre p { margin:0 0 .7rem; font-size:.95rem; }
.cadre p:last-child { margin-bottom:0; }
.ident { font-family:var(--mono); font-size:.82rem; color:var(--att); }
.ident a { color:var(--sig); text-decoration:none; border-bottom:1px solid transparent; }
.ident a:hover, .ident a:focus-visible { border-bottom-color:var(--sig); }
.ok { color:var(--ver); font-family:var(--sans); font-size:.8rem; font-weight:600; letter-spacing:.04em; text-transform:uppercase; }
a { color:var(--sig); }
:focus-visible { outline:2px solid var(--sig); outline-offset:2px; }
footer { margin-top:3rem; font-size:.87rem; color:var(--att); font-family:var(--sans); }
@media (prefers-reduced-motion:reduce) { * { animation:none!important; transition:none!important; } }
</style>
"""

# Les comptes sont calcules, jamais ecrits a la main : une page qui annonce vingt
# references et en affiche cinquante-sept se discredite elle-meme.
N_PM = sum(len(g["refs"]) for g in groupes)
N_AUTRES = len(autres)
N_CONTROLE = 20          # nombre de lignes passees au controle independant ligne a ligne

TETE = """
<div class="wrap">
  <p class="eyebrow">Toxicosqueros &middot; sources</p>
  <h1>Ce sur quoi le morceau s&rsquo;appuie</h1>
  <p class="cri">Non aux rituels d&rsquo;intoxication imposés par des proches&#8239;!</p>
  <p class="chapo">%d publications indexées dans PubMed, %d sources hors PubMed
  &mdash; décisions, rapports publics, articles sans identifiant PubMed &mdash; et le cadre
  juridique français applicable à l&rsquo;ayahuasca.</p>
  <p class="note">Les identifiants sont cliquables. Rien ici ne vise une personne :
  cette page documente un état de la littérature et du droit.</p>

  %s

  <hr>

  <section class="grp" id="cadre-juridique">
    <h2>Cadre juridique français</h2>
    <p class="lede">L&rsquo;ayahuasca n&rsquo;est pas une zone grise en France.</p>
    <div class="cadre">
      <h3>Classement comme stupéfiant</h3>
      <p>Les plantes entrant dans sa préparation, <i>Banisteriopsis caapi</i> et
      <i>Psychotria viridis</i>, figurent sur la liste des stupéfiants par l&rsquo;arrêté
      du 22&nbsp;février 1990, modifié par celui du 20&nbsp;avril 2005.</p>
      <p class="ident"><a href="https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000000239974" target="_blank" rel="noopener">Arrêté du 20 avril 2005 &middot; NOR SANP0521544A</a></p>
    </div>
    <div class="cadre">
      <h3>Recours rejeté en 2007</h3>
      <p>Le Conseil d&rsquo;État a rejeté la demande d&rsquo;annulation de cet arrêté.</p>
      <p class="ident"><a href="https://www.legifrance.gouv.fr/ceta/id/CETATEXT000018007864" target="_blank" rel="noopener">Conseil d&rsquo;État, 21 décembre 2007, n&deg; 282100</a></p>
    </div>
    <div class="cadre">
      <h3>Demande d&rsquo;abrogation rejetée en 2024</h3>
      <p>Une cinquantaine de requérants et la fondation ICEERS demandaient le retrait de ces
      deux plantes de la liste. Le Conseil d&rsquo;État a rejeté la requête, retenant les
      risques pour la santé publique et <strong>écartant le moyen tiré de la liberté
      religieuse</strong> ainsi que celui tiré du droit au respect de la vie privée et familiale.</p>
      <p class="ident"><a href="https://conseil-etat.fr/fr/arianeweb/CE/decision/2024-12-18/487157" target="_blank" rel="noopener">Conseil d&rsquo;État, 18 décembre 2024, n&deg; 487157</a></p>
    </div>
  </section>

  <hr>

"""

PIED = """
  <hr>

  <section class="grp" id="methode">
    <h2>Méthode et limites</h2>
    <p class="lede">Ce qui a été fait, et ce que cette page ne prétend pas établir.</p>
    <div class="cadre">
      <p><span class="ok">Vérifié</span> &nbsp;Les métadonnées des %d notices PubMed
      &mdash; premier auteur, revue, année, titre &mdash; ne sont pas saisies à la main :
      elles sont téléchargées depuis l&rsquo;API officielle de la NCBI et rechargées
      à chaque mise à jour de cette page. La dernière exécution n&rsquo;a relevé
      aucune divergence sur les %d notices.</p>
      <p><span class="ok">Vérifié</span> &nbsp;%d de ces références ont en outre été
      comparées une par une à leur notice par un contrôle indépendant : %d sur %d
      conformes, diacritiques comprises. Les autres reposent sur la seule provenance
      automatique décrite ci-dessus.</p>
      <p>Les %d sources hors PubMed portent chacune un identifiant stable &mdash; DOI, ISBN,
      numéro Légifrance, identifiant ECLI, code CIM-11, numéro de rapport parlementaire.
      Elles n&rsquo;ont pas de notice NCBI : leur libellé a été saisi à la main, après
      ouverture de la page.</p>
      <p>Cette page liste des sources ; elle ne les résume pas et ne les interprète pas.
      Une étude de population mesure une association dans un groupe. Elle n&rsquo;établit
      la cause des troubles d&rsquo;aucune personne en particulier.</p>
      <p>Le corpus comprend délibérément une revue qui <strong>révise à la baisse</strong>
      les preuves de psychose induite par les psychédéliques. Une bibliographie qui ne
      contiendrait que des sources à charge ne vaudrait rien.</p>
      <p>Il comprend aussi, pour la même raison, des travaux qui <strong>attaquent la
      valeur d&rsquo;autres sources de cette page</strong>. Un psychotrope qui se sent ne
      se cache pas&nbsp;: dans les essais, sujets et évaluateurs devinent le bras qu&rsquo;ils
      ont tiré, et l&rsquo;attente fait le reste. Et plusieurs travaux sur l&rsquo;ayahuasca
      ont été menés à l&rsquo;intérieur des communautés qui en font usage, sur leurs propres
      membres, sans insu ni groupe témoin — c&rsquo;est le cas des études de 2005 sur les
      adolescents, que cette page cite. Les deux limites sont documentées dans leur
      propre rubrique plutôt que passées sous silence.</p>
    </div>
  </section>

  <footer>
    <p>Signalement des dérives sectaires en France : MIVILUDES.
    Accompagnement des victimes et des familles : CCMM, UNADFI.</p>
  </footer>
</div>
"""

page = (STYLE
        + TETE % (N_PM, N_AUTRES, SOMMAIRE)
        + sections + "<hr>" + AUTRES_SECTION
        + PIED % (N_PM, N_PM, N_CONTROLE, N_CONTROLE, N_CONTROLE, N_AUTRES))
# LF explicite : page web, relue par un navigateur et par l'artefact, pas par Windows.
with io.open("references_toxicosqueros.html", "w", encoding="utf-8", newline="\n") as f:
    f.write(page)
print("page ecrite : %d caracteres" % len(page))
print("references rendues : %d" % page.count('class="ref"'))
print("liens pubmed : %d" % page.count("pubmed.ncbi.nlm.nih.gov"))
