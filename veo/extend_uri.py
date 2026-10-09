#!/usr/bin/env python3
"""Etend un plan deja genere, a partir de l'URI conserve dans uris.json.

    .venv/Scripts/python.exe extend_uri.py <cle> <sortie.mp4> ["texte rappe"]

La cle est celle notee par chain_shot.py, par exemple "prompts_5chanteurs:01".
Sans argument de cle, liste ce qui est disponible.

Interet : la base est deja payee. Relancer une extension avec un autre texte
ou un autre mouvement ne coute que l'extension, tant que l'URI n'a pas expire (48 h).
"""
import json
import os
import pathlib
import sys

from google import genai
from google.genai import types

import generate

MODEL = "veo-3.1-fast-generate-preview"
URIS = pathlib.Path(__file__).resolve().parent / "uris.json"

STYLE = (
    "Cinematic, 35mm anamorphic, shallow depth of field, thick atmospheric haze, high "
    "contrast, desaturated steel-blue base with toxic green and violet practical lights, "
    "fine film grain, handheld with slow drift. "
    "No on-screen text, no subtitles, no captions, no watermark."
)


def suite(texte):
    base = ("The shot continues without a cut, same person, same place, same light. "
            "He keeps rapping straight to camera without pause, breathing hard between "
            "lines. The camera pushes slowly closer until his face fills the frame. ")
    if texte:
        base += 'He raps in French straight to camera: "%s" ' % texte
    return base + STYLE


def main():
    d = json.loads(URIS.read_text(encoding="utf-8")) if URIS.exists() else {}
    if len(sys.argv) < 3:
        print("cles disponibles :")
        for k, v in d.items():
            print("  %-28s note le %s" % (k, v.get("vu")))
        sys.exit(__doc__ if not d else 0)

    cle, dst = sys.argv[1], pathlib.Path(sys.argv[2])
    texte = sys.argv[3] if len(sys.argv) > 3 else None
    if cle not in d:
        sys.exit("cle inconnue : %s" % cle)

    generate.load_env()
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        sys.exit("GEMINI_API_KEY absente.")

    print("extension depuis %s -> ~0.70 USD" % cle)
    client = genai.Client()
    op = client.models.generate_videos(
        model=MODEL,
        source=types.GenerateVideosSource(prompt=suite(texte),
                                          video=types.Video(uri=d[cle]["uri"])),
        config=types.GenerateVideosConfig(
            aspect_ratio="16:9", resolution="720p", duration_seconds="8",
            person_generation="allow_all"),
    )
    op = generate.poll(client, op, "extension", 900)
    v = generate.videos_of(op)
    if not v:
        sys.exit("refus : %s" % (generate.refusal_reason(op) or "motif non renvoye"))
    client.files.download(file=v[0].video, destination=str(dst))
    print("OK -> %s  (contient la base)" % dst.name)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()
