#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fabrique le carton de fin « mot d'ordre » et l'ajoute au film.

    python carton_cri.py          # fabrique le carton, n'ajoute rien
    python carton_cri.py --go     # fabrique le carton ET ecrit le film rallonge

Le film d'origine n'est jamais ecrase : la version rallongee s'appelle
TOXICOSQUEROS_final_cri.mp4. La concatenation se fait en copie de flux, donc
les 150 s deja montees ne sont pas reencodees et la synchro son reste celle,
mesuree, du montage existant.

Deux choses a savoir si on reprend ce fichier :

- La police est celle, par defaut, de melt : c'est exactement celle du carton
  du refrain. Ne pas la specifier est volontaire. En imposer une casserait
  l'accord entre les deux cartons.
- Les fondus font 4 images de chaque cote, comme tous les plans de _fade/.
  Seule la toute premiere image est entierement noire ; les trois suivantes
  montent. C'est la convention du montage, mesuree sur les clips existants.
"""
import pathlib
import subprocess
import sys

ICI = pathlib.Path(__file__).resolve().parent
SHOTCUT = pathlib.Path(r"C:/Program Files/Shotcut")
MELT, FFMPEG, FFPROBE = (SHOTCUT / "melt.exe", SHOTCUT / "ffmpeg.exe",
                         SHOTCUT / "ffprobe.exe")

FILM = ICI / "TOXICOSQUEROS_final.mp4"
CARTON = ICI / "_fade" / "20_cri.mp4"
MUET = ICI / "_cri_muet.mp4"
SORTIE = ICI / "TOXICOSQUEROS_final_cri.mp4"
LISTE = ICI / "_liste_cri.txt"

IPS = 24
IMAGES = 96                      # 4,000 s
FONDU = 4.0 / IPS                # 4 images, comme tout le montage
DUREE = IMAGES / float(IPS)

# Apostrophe typographique U+2019 et espace fine insecable U+202F avant le « ! » :
# c'est un texte compose, pas un formulaire web. La regle de l'Imprimerie nationale
# veut une fine insecable devant ! ? et ; — insecable, pour que le signe ne tombe
# jamais seul en debut de ligne.
LIGNES = [u"Non aux rituels d\u2019intoxication",
          u"impos\u00e9s par des proches\u202f!"]

TAILLE = 64                      # mesure sur le carton du refrain
CENTRES = [480, 600]             # deux lignes, 120 px d'ecart, bloc centre sur 540


def courir(cmd, quoi):
    r = subprocess.run([str(c) for c in cmd], capture_output=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode("utf-8", "replace")[-2000:])
        sys.exit("echec : %s" % quoi)


def champ(f, flux, quoi):
    r = subprocess.run([str(FFPROBE), "-v", "error", "-select_streams", flux,
                        "-show_entries", quoi, "-of", "csv=p=0", str(f)],
                       capture_output=True)
    return r.stdout.decode().strip().splitlines()[0] if r.stdout.strip() else ""


def sonde(f):
    """Chaque flux est interroge separement : sinon l'audio ecrase la video
    et on croit lire 96 images la ou ffprobe repond 26 paquets AAC."""
    return {
        "duree": champ(f, "v:0", "format=duration"),
        "images": champ(f, "v:0", "stream=nb_frames"),
        "duree_son": champ(f, "a:0", "stream=duration"),
    }


def rendre_texte():
    cmd = [MELT, "-profile", "atsc_1080p_24", "color:black", "out=%d" % (IMAGES - 1)]
    for ligne, y in zip(LIGNES, CENTRES):
        cmd += ["-filter", "dynamictext",
                u"argument=%s" % ligne,
                "size=%d" % TAILLE, "weight=700",
                "fgcolour=0xffffffff", "valign=middle", "halign=center",
                "geometry=0 %d 1920 90" % (y - 45)]
    cmd += ["-consumer", "avformat:%s" % MUET,
            "vcodec=libx264", "crf=16", "pix_fmt=yuv420p", "an=1",
            "terminate_on_pause=1"]
    courir(cmd, "rendu du texte par melt")


def habiller():
    """Fondus, piste muette, et exactement les memes parametres que le film."""
    CARTON.parent.mkdir(exist_ok=True)
    courir([FFMPEG, "-v", "error",
            "-i", MUET,
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-vf", "fade=t=in:st=0:d=%.6f,fade=t=out:st=%.6f:d=%.6f"
                   % (FONDU, DUREE - FONDU, FONDU),
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
            "-crf", "18", "-preset", "veryslow", "-pix_fmt", "yuv420p", "-r", "24",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            # Surtout PAS de -frames:v ici. Il cloture la sortie des que le compte
            # d'images est atteint, et le silence reste tronque a une demi-seconde :
            # un trou de son a la jonction, qu'on ne voit pas passer tant qu'on n'a
            # pas regarde le film jusqu'au bout. -t borne proprement les deux flux,
            # et la source melt faisant deja 96 images pile, le compte tombe juste.
            "-t", "%.6f" % DUREE, "-movflags", "+faststart",
            "-y", CARTON], "habillage du carton")


def coller():
    LISTE.write_text("file '%s'\nfile '%s'\n"
                     % (FILM.name, CARTON.relative_to(ICI).as_posix()),
                     encoding="utf-8", newline="\n")
    # Copie de flux : le film deja monte n'est pas retouche d'un seul bit.
    courir([FFMPEG, "-v", "error", "-f", "concat", "-safe", "0",
            "-i", LISTE, "-c", "copy", "-movflags", "+faststart",
            "-y", SORTIE], "concatenation")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    go = "--go" in sys.argv[1:]
    for outil in (MELT, FFMPEG, FFPROBE):
        if not outil.exists():
            sys.exit("outil introuvable : %s" % outil)
    if not FILM.exists():
        sys.exit("film introuvable : %s" % FILM)

    print(u"carton : %s" % u" / ".join(LIGNES))
    rendre_texte()
    habiller()
    d = sonde(CARTON)
    print(u"%s : %s s video, %s images, %s s de son"
          % (CARTON.name, d["duree"], d["images"], d["duree_son"]))

    # Controle, parce que la panne est muette : un carton sans son se colle
    # sans erreur et ne se remarque qu'a la lecture.
    ennuis = []
    if int(d["images"]) != IMAGES:
        ennuis.append("%s images au lieu de %d" % (d["images"], IMAGES))
    if abs(float(d["duree_son"]) - DUREE) > 0.05:
        ennuis.append("son de %s s au lieu de %.3f s" % (d["duree_son"], DUREE))
    if ennuis:
        sys.exit("carton inutilisable : " + " ; ".join(ennuis))

    avant = sonde(FILM)
    print(u"%s : %s s" % (FILM.name, avant["duree"]))
    if not go:
        print(u"\nRien n'a ete colle. Relance avec --go pour ecrire %s" % SORTIE.name)
        sys.exit(0)

    coller()
    apres = sonde(SORTIE)
    print(u"%s : %s s, %s images" % (SORTIE.name, apres["duree"], apres["images"]))
    attendu = float(avant["duree"]) + DUREE
    ecart = abs(float(apres["duree"]) - attendu)
    print(u"attendu %.3f s, ecart %.3f s %s"
          % (attendu, ecart, u"" if ecart < 0.01 else u"  <<< A VERIFIER"))
