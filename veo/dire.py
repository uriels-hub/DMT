#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fait dire le texte par Piper, plan par plan, et compare au temps disponible.

    .venv/Scripts/python.exe dire.py           # les 18 plans, mesure seule
    .venv/Scripts/python.exe dire.py --wav     # ecrit aussi un wav par plan
    .venv/Scripts/python.exe dire.py --wav 18  # seulement le plan 18
    .venv/Scripts/python.exe dire.py --piste   # une seule bande calee sur le film

A QUOI CELA SERT, ET A QUOI CELA NE SERT PAS

Cela repond a une question et une seule : le texte tient-il dans ses huit
secondes ? Le plan 18 demande six syllabes par seconde — est-ce humainement
prononçable, ou faut-il couper ?

Piper LIT, il ne rappe pas. Le resultat ne dit rien du flow, de l'accentuation
ni du phrase. Une voix de synthese a une cadence plate, la ou un interprete
accelere et retient. Lue ici, une mesure trop longue le sera aussi en studio ;
une mesure qui passe de justesse chez Piper peut tres bien passer a l'aise
chez un interprete. L'outil detecte le debordement, pas l'aisance.

LA NOTATION N'EST PAS LISIBLE PAR UNE MACHINE

« Go~uu~urou », « &spoir », « v€rgogn€ » seraient massacres tels quels. La
table prononciation.json dit ce que chaque graphie devient. Deux entrees y
sont marquees "sur": false — ce sont mes lectures, pas celles de l'auteur.
Les corriger est la premiere chose a faire, et cela oblige a ecrire noir sur
blanc ce que chaque marque fait au temps, ce qui vaut en soi.
"""
import json
import pathlib
import re
import sys
import wave

ICI = pathlib.Path(__file__).resolve().parent
VOIX = ICI / "voix" / "fr_FR-tom-medium.onnx"
SORTIE = ICI / "dit"
FENETRE = 8.0


def table():
    t = json.loads((ICI / "prononciation.json").read_text(encoding="utf-8"))
    doute = [m for m in t["mots"] if not m.get("sur")]
    return t, doute


def prononçable(v, t):
    """Le vers, debarrasse de sa notation, tel qu'une machine peut le lire."""
    for m in t["mots"]:
        v = v.replace(m["ecrit"], m["dit"])
    for e in t["emoji"]:
        v = v.replace(e, u", " if t["emoji"][e] else u" ")
    for s, r in t["signes"].items():
        if not s.startswith(u"_"):
            v = v.replace(s, r)
    v = re.sub(u"\\s*\u25b6\\s*", u" ", v)
    return re.sub(u"\\s{2,}", u" ", v).strip()


FFMPEG = pathlib.Path(r"C:/Program Files/Shotcut/ffmpeg.exe")
PISTE = ICI / "piste_guide.wav"
DEBUT = 4.0        # le carton d'avertissement ouvre le film
DUREE = 163.0      # duree du film de diffusion


def piste(plans):
    """Assemble les 18 wav en une bande calee sur le film.

    Chaque plan est pose au debut de sa fenetre, pas etire pour la remplir :
    on veut voir ou la parole deborde, pas la faire rentrer de force.
    """
    import subprocess
    manquants = [p["n"] for p in plans if not (SORTIE / ("plan_%02d.wav" % p["n"])).exists()]
    if manquants:
        sys.exit("wav manquants : %s — lancer d'abord dire.py --wav"
                 % ", ".join(str(x) for x in manquants))
    if not FFMPEG.exists():
        sys.exit("ffmpeg introuvable : %s" % FFMPEG)
    cmd, f = [str(FFMPEG), "-v", "error"], []
    for i, p in enumerate(plans):
        cmd += ["-i", str(SORTIE / ("plan_%02d.wav" % p["n"]))]
        ms = int(round((DEBUT + (p["n"] - 1) * FENETRE) * 1000))
        f.append("[%d]aresample=48000,aformat=channel_layouts=stereo,"
                 "adelay=%d|%d[a%d]" % (i, ms, ms, i))
    # apad apres amix : amix s'arrete au dernier son, et -t tronque sans completer.
    # Sans lui la piste finit a 151 s et ne se cale plus sur le film.
    cmd += ["-filter_complex",
            ";".join(f) + ";" + "".join("[a%d]" % i for i in range(len(plans)))
            + "amix=inputs=%d:normalize=0:dropout_transition=0[m];[m]apad[o]" % len(plans),
            "-map", "[o]", "-t", "%.3f" % DUREE,
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", "-y", str(PISTE)]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode:
        sys.stderr.write(r.stderr.decode("utf-8", "replace")[-1200:])
        sys.exit("assemblage de la piste echoue")
    with wave.open(str(PISTE), "rb") as w:
        d = w.getnframes() / float(w.getframerate())
    print(u"\n  %s : %.3f s, %d Hz, %d voies"
          % (PISTE.name, d, 48000, 2))
    print(u"  les 18 plans sont poses a 4, 12, 20 ... 140 s, non etires.")
    print(u"  a poser sous %s pour entendre le calage."
          % "montage/TOXICOSQUEROS_diffusion.mp4")


def main():
    args = sys.argv[1:]
    faire_piste = "--piste" in args
    faire_wav = "--wav" in args or faire_piste
    seul = next((int(a) for a in args if a.isdigit()), None)

    if not VOIX.exists():
        sys.exit("voix absente : %s\n"
                 "  .venv/Scripts/python.exe -m piper.download_voices "
                 "fr_FR-tom-medium --data-dir voix" % VOIX)
    d = json.loads((ICI / "temps_data.json").read_text(encoding="utf-8"))
    t, doute = table()
    if doute:
        print(u"ATTENTION — %d lecture(s) non confirmee(s) dans prononciation.json :" % len(doute))
        for m in doute:
            print(u"   %-14s lu « %s »" % (m["ecrit"], m["dit"]))
        print()

    from piper import PiperVoice
    v = PiperVoice.load(str(VOIX))
    sr = v.config.sample_rate
    if faire_wav:
        SORTIE.mkdir(exist_ok=True)

    print(u"%-5s %5s %6s %6s %7s   %s" % (u"plan", u"syl", u"dispo", u"dit", u"marge", u"etat"))
    print(u"-" * 74)
    deborde, total = [], 0.0
    for p in d["plans"]:
        if seul and p["n"] != seul:
            continue
        vers = [x for x in d["vers"] if x["plan"] == p["n"]]
        texte = u" ".join(prononçable(x["fr"], t) for x in vers)
        chemin = SORTIE / ("plan_%02d.wav" % p["n"]) if faire_wav else None
        if chemin:
            with wave.open(str(chemin), "wb") as w:
                v.synthesize_wav(texte, w)
            with wave.open(str(chemin), "rb") as w:
                duree = w.getnframes() / float(w.getframerate())
        else:
            n = sum(len(c.audio_int16_bytes) for c in v.synthesize(texte))
            duree = n / float(sr * 2)
        total += duree
        marge = FENETRE - duree
        etat = u"tient" if marge >= 0.4 else (u"juste" if marge >= 0 else u"DEBORDE")
        if marge < 0:
            deborde.append((p["n"], -marge))
        print(u"%-5d %5d %6.1f %6.2f %+7.2f   %s"
              % (p["n"], p["syl"], FENETRE, duree, marge, etat))

    if seul:
        return
    print()
    print(u"  total dit : %.1f s pour %.0f s disponibles" % (total, 18 * FENETRE))
    if deborde:
        print(u"  %d plan(s) debordent :" % len(deborde))
        for n, x in sorted(deborde, key=lambda z: -z[1]):
            print(u"    plan %-2d  %+.2f s de trop" % (n, x))
    else:
        print(u"  aucun plan ne deborde.")
    if faire_wav:
        print(u"\n  wav ecrits dans %s/" % SORTIE.name)
    if faire_piste:
        piste(d["plans"])


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()
