#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fabrique les cartons d'avertissement et assemble le film definitif.

    python cartons.py          # fabrique les cartons, n'assemble rien
    python cartons.py --go     # fabrique ET ecrit TOXICOSQUEROS_diffusion.mp4

Le film passe de 154 a 163 secondes :

    0,000 -   4,000   avertissement : images generees, personne n'est reel
    4,000 - 148,000   les 18 plans
  148,000 - 154,000   carton du refrain
  154,000 - 158,000   carton du mot d'ordre
  158,000 - 163,000   ou signaler, ou se faire aider

CONSEQUENCE A NE PAS OUBLIER : le carton de tete decale tout le film de 4 s.
Les neuf sous-titres doivent etre regeneres avec DECALAGE = 4.0 dans srt.py,
sinon ils tombent quatre secondes trop tot sur toute la duree.

Le carton de tete dit ce que YouTube impose de declarer de toute facon a la mise
en ligne (contenu synthetique realiste) : le declarer deux fois ne coute rien,
ne pas le declarer coute une sanction.

Le carton de queue ne porte pas d'URL. Une adresse a l'ecran n'est pas cliquable
et celle du formulaire de la MIVILUDES fait 99 caracteres : illisible. On nomme
les organismes, les liens sont en description.
"""
import pathlib
import subprocess
import sys

ICI = pathlib.Path(__file__).resolve().parent
SHOTCUT = pathlib.Path(r"C:/Program Files/Shotcut")
MELT, FFMPEG, FFPROBE = SHOTCUT / "melt.exe", SHOTCUT / "ffmpeg.exe", SHOTCUT / "ffprobe.exe"

FILM = ICI / "_master_net.mp4"            # 154 s, masterise, compteur retire
SORTIE = ICI / "TOXICOSQUEROS_diffusion.mp4"
LISTE = ICI / "_liste_diffusion.txt"

IPS = 24
FONDU = 4.0 / IPS

# Deux cartons. Le premier ouvre, le second ferme.
CARTONS = [
    {
        "nom": "00_avertissement",
        "secondes": 4.0,
        "taille": 54,
        "lignes": [
            u"Images et voix g\u00e9n\u00e9r\u00e9es par intelligence artificielle.",
            u"Aucun interpr\u00e8te n\u2019est une personne r\u00e9elle,",
            u"aucun lieu n\u2019existe.",
            u"Seuls les textes sont de l\u2019auteur.",
        ],
    },
    {
        "nom": "21_ressources",
        "secondes": 5.0,
        "taille": 50,
        "lignes": [
            u"Signaler une d\u00e9rive sectaire\u202f: MIVILUDES",
            u"",
            u"Aide aux victimes et aux familles\u202f:",
            u"CCMM, UNADFI",
            u"",
            u"Liens en description.",
        ],
    },
]


def courir(cmd, quoi):
    r = subprocess.run([str(c) for c in cmd], capture_output=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode("utf-8", "replace")[-1500:])
        sys.exit("echec : %s" % quoi)


def champ(f, flux, quoi):
    r = subprocess.run([str(FFPROBE), "-v", "error", "-select_streams", flux,
                        "-show_entries", quoi, "-of", "csv=p=0", str(f)],
                       capture_output=True)
    s = r.stdout.decode().strip().splitlines()
    return s[0] if s else ""


def fabriquer(c):
    images = int(round(c["secondes"] * IPS))
    muet = ICI / ("_%s_muet.mp4" % c["nom"])
    final = ICI / "_fade" / ("%s.mp4" % c["nom"])
    final.parent.mkdir(exist_ok=True)

    # Bloc centre verticalement. Les lignes vides servent d'interligne.
    n = len(c["lignes"])
    pas = 78
    haut = 540 - (n - 1) * pas / 2.0
    cmd = [MELT, "-profile", "atsc_1080p_24", "color:black", "out=%d" % (images - 1)]
    for i, ligne in enumerate(c["lignes"]):
        if not ligne:
            continue
        cmd += ["-filter", "dynamictext", u"argument=%s" % ligne,
                "size=%d" % c["taille"], "weight=700",
                "fgcolour=0xffffffff", "valign=middle", "halign=center",
                "geometry=0 %d 1920 90" % int(haut + i * pas - 45)]
    cmd += ["-consumer", "avformat:%s" % muet, "vcodec=libx264", "crf=16",
            "pix_fmt=yuv420p", "an=1", "terminate_on_pause=1"]
    courir(cmd, "rendu de %s" % c["nom"])

    # Jamais -frames:v avec une piste son : il cloture avant que l'audio soit
    # ecrit et laisse un trou a la jonction. -t borne proprement les deux flux.
    courir([FFMPEG, "-v", "error", "-i", muet,
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-vf", "fade=t=in:st=0:d=%.6f,fade=t=out:st=%.6f:d=%.6f"
                   % (FONDU, c["secondes"] - FONDU, FONDU),
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
            "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-r", "24",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
            "-t", "%.6f" % c["secondes"], "-movflags", "+faststart",
            "-y", final], "habillage de %s" % c["nom"])
    muet.unlink(missing_ok=True)

    img = int(champ(final, "v:0", "stream=nb_frames") or 0)
    son = float(champ(final, "a:0", "stream=duration") or 0)
    if img != images or abs(son - c["secondes"]) > 0.05:
        sys.exit("%s inutilisable : %d images, %.3f s de son" % (c["nom"], img, son))
    print(u"  %-18s %5.3f s  %3d images  son %.3f s"
          % (final.name, float(champ(final, "v:0", "format=duration")), img, son))
    return final


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if not FILM.exists():
        sys.exit("film introuvable : %s" % FILM)

    print(u"cartons")
    faits = [fabriquer(c) for c in CARTONS]

    duree = float(champ(FILM, "v:0", "format=duration"))
    total = duree + sum(c["secondes"] for c in CARTONS)
    print(u"\n%s : %.3f s" % (FILM.name, duree))
    print(u"film de diffusion attendu : %.3f s" % total)

    if "--go" not in sys.argv[1:]:
        print(u"\nRien n'a ete assemble. Relance avec --go.")
        print(u"Ne pas oublier : DECALAGE = 4.0 dans srt.py, puis maj.py srt.")
        sys.exit(0)

    LISTE.write_text(
        "file '_fade/%s.mp4'\nfile '%s'\nfile '_fade/%s.mp4'\n"
        % (CARTONS[0]["nom"], FILM.name, CARTONS[1]["nom"]),
        encoding="utf-8", newline="\n")
    courir([FFMPEG, "-v", "error", "-f", "concat", "-safe", "0", "-i", LISTE,
            "-c", "copy", "-movflags", "+faststart", "-y", SORTIE],
           "assemblage")

    d = float(champ(SORTIE, "v:0", "format=duration"))
    img = champ(SORTIE, "v:0", "stream=nb_frames")
    ecart = abs(d - total)
    print(u"\n%s : %.3f s, %s images" % (SORTIE.name, d, img))
    print(u"attendu %.3f s, ecart %.3f s%s"
          % (total, ecart, u"" if ecart < 0.01 else u"   <<< A VERIFIER"))
    print(u"\nMaintenant : DECALAGE = 4.0 dans srt.py, puis maj.py srt.")
