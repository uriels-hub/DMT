#!/usr/bin/env python3
"""Extension de 8 s d'une video existante, via veo-3.1-fast.

    .venv/Scripts/python.exe extend.py <source.mp4> <sortie.mp4>

Lite ne sait pas etendre : il faut fast (0,12 $/s en 1080p) ou la version pleine.
La source part en octets dans l'appel, d'ou la necessite de n'envoyer que la queue.
"""
import json
import os
import pathlib
import sys
import time

from google import genai
from google.genai import types

import generate  # reutilise load_env, poll, videos_of, refusal_reason

MODEL = "veo-3.1-fast-generate-preview"
PRIX = 0.12  # par seconde, 1080p

SUITE = (
    "The shot continues without a cut. The man with short twisted locs and the wooden "
    "bead necklace keeps rapping straight to camera, breathing hard between lines. The "
    "broken chains behind him swing wider and start to fall away one by one into the "
    "smoke. The ghost faces in double exposure dissolve and are replaced by tropical "
    "foliage closing in from both edges of frame. The camera pushes slowly closer until "
    "his face fills the frame, then holds. "
    "Cinematic, 35mm anamorphic, shallow depth of field, thick atmospheric haze, high "
    "contrast, desaturated steel-blue base with toxic green and violet practical lights, "
    "fine film grain, handheld with slow drift. "
    "No on-screen text, no subtitles, no captions, no watermark."
)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    if not src.exists():
        sys.exit("source introuvable: %s" % src)

    generate.load_env()
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        sys.exit("GEMINI_API_KEY absente.")

    print("modele : %s, 8 s -> %.2f USD" % (MODEL, 8 * PRIX))
    client = genai.Client()

    # Le Developer API refuse la video en octets (`encodedVideo`) : il faut un URI.
    # L'API Files en fournit un, et il est accepte.
    f = client.files.upload(file=str(src))
    for _ in range(30):
        f = client.files.get(name=f.name)
        if str(getattr(f, "state", "")).endswith("ACTIVE"):
            break
        time.sleep(2)
    print("source : %s -> %s (%s)" % (src.name, f.uri, f.state))
    config = types.GenerateVideosConfig(
        aspect_ratio="16:9",
        resolution="1080p",
        duration_seconds="8",
        person_generation="allow_all",   # allow_adult est refuse en extension
    )
    source = types.GenerateVideosSource(prompt=SUITE, video=types.Video(uri=f.uri))

    print("envoi...")
    op = client.models.generate_videos(model=MODEL, source=source, config=config)
    op = generate.poll(client, op, "extension", 900)

    vids = generate.videos_of(op)
    if not vids:
        sys.exit("refus: %s" % (generate.refusal_reason(op) or "motif non renvoye"))
    client.files.download(file=vids[0].video, destination=str(dst))
    print("OK -> %s" % dst)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()
