#!/usr/bin/env python3
"""Genere un plan d'un fichier de prompts en 720p, puis l'etend de 7 s.

    .venv/Scripts/python.exe chain_shot.py <prompts.json> <id> <sortie_sans_extension>

Le resultat de l'extension contient DEJA la base : un seul fichier de 15 s.

Contraintes constatees (aucune documentee) :
  - modele : lite ne sait pas etendre, il faut fast
  - resolution : 720p obligatoire, une base 1080p est refusee a l'extension
  - video : ni `mime_type` (-> encoding), ni octets (-> encodedVideo). URI seulement.
  - l'URI ne vient que d'une generation Veo, et vit 48 h
  - person_generation : allow_adult avec une image, allow_all en extension
"""
import json
import os
import pathlib
import sys
import time

from google import genai
from google.genai import types

import generate

MODEL = "veo-3.1-fast-generate-preview"
PRIX = 0.10
URIS = pathlib.Path(__file__).resolve().parent / "uris.json"

SUITE = (
    "The shot continues without a cut, same person, same place, same light. He stops "
    "rapping and holds the stare straight into the lens, breathing hard. The smoke "
    "thickens around him and the camera pushes slowly closer until his face fills the "
    "frame, then holds still. No new dialogue, he does not speak."
)


def noter(uri, quoi):
    """Sans l'URI conserve, l'extension devient impossible des la session suivante."""
    d = json.loads(URIS.read_text(encoding="utf-8")) if URIS.exists() else {}
    d[quoi] = {"uri": uri, "vu": time.strftime("%Y-%m-%d %H:%M"), "expire_sous": "48 h"}
    URIS.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def attendre(client, op, nom):
    op = generate.poll(client, op, nom, 900)
    v = generate.videos_of(op)
    if not v:
        sys.exit("%s refuse : %s" % (nom, generate.refusal_reason(op) or "motif non renvoye"))
    return v[0].video


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    src, sid, dst = pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3])
    data = json.loads(src.read_text(encoding="utf-8"))
    shot = next((s for s in data["shots"] if s["id"] == sid), None)
    if not shot:
        sys.exit("plan %s introuvable dans %s" % (sid, src.name))

    generate.load_env()
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        sys.exit("GEMINI_API_KEY absente.")

    prompt = generate.build_prompt(shot, data["suffix"])
    image = generate.load_first_frame(shot)
    print("%s plan %s, 8 s + extension -> %.2f USD" % (MODEL, sid, 15 * PRIX))
    client = genai.Client()

    print("[1/2] base 720p%s..." % (" (premiere frame)" if image is not None else ""))
    op = client.models.generate_videos(
        model=MODEL,
        source=types.GenerateVideosSource(prompt=prompt, image=image),
        config=types.GenerateVideosConfig(
            aspect_ratio="16:9", resolution="720p", duration_seconds="8",
            person_generation="allow_adult" if image is not None else "allow_all"),
    )
    v1 = attendre(client, op, "base")
    uri = getattr(v1, "uri", None)
    if not uri:
        sys.exit("pas d'URI renvoye : extension impossible")
    noter(uri, "%s:%s" % (src.stem, sid))
    print("      URI note dans uris.json")
    a = dst.with_name(dst.name + "_base.mp4")
    client.files.download(file=v1, destination=str(a))
    print("      -> %s" % a.name)

    print("[2/2] extension...")
    op = client.models.generate_videos(
        model=MODEL,
        source=types.GenerateVideosSource(prompt=SUITE, video=types.Video(uri=uri)),
        config=types.GenerateVideosConfig(
            aspect_ratio="16:9", resolution="720p", duration_seconds="8",
            person_generation="allow_all"),
    )
    v2 = attendre(client, op, "extension")
    b = dst.with_name(dst.name + "_15s.mp4")
    client.files.download(file=v2, destination=str(b))
    print("      -> %s  (contient la base)" % b.name)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()
