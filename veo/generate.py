#!/usr/bin/env python3
"""TOXICOSQUEROS - generation par lot sur Veo 3.1 Lite (Gemini API).

    pip install google-genai
    set GEMINI_API_KEY=...        (Windows)   /   export GEMINI_API_KEY=...

    python generate.py                 # les 18 plans, reprend ce qui manque
    python generate.py --only 03 07    # seulement ces plans
    python generate.py --take 2        # 2e prise -> out/03_take2.mp4
    python generate.py --dry-run       # affiche les prompts et le cout, n'appelle rien
"""
import argparse
import json
import os
import pathlib
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from google import genai
from google.genai import types

MODELS = {
    "lite": "veo-3.1-lite-generate-preview",
    "fast": "veo-3.1-fast-generate-preview",
    "full": "veo-3.1-generate-preview",
}
PRICE_PER_SEC = {
    "lite": {"720p": 0.05, "1080p": 0.08},
    "fast": {"720p": 0.10, "1080p": 0.12, "4k": 0.30},
    "full": {"720p": 0.40, "1080p": 0.40, "4k": 0.60},
}
# Contraintes constatees, pas toutes documentees :
#   lite : pas de 4K, pas d'images de reference, negative_prompt refuse (400)
#   4K   : duree 8 s obligatoire
#   person_generation : allow_adult avec image, allow_all en texte seul

# Veo a tendance a incruster des sous-titres des qu'on lui donne du dialogue.
# Mais veo-3.1-lite le refuse : 400 "`negativePrompt` isn't supported by this model".
# Garde pour --negative si tu passes en veo-3.1 ou veo-3.1-fast. Sinon, c'est la
# fin du suffixe dans prompts.json qui fait le travail, moins bien.
NEGATIVE = ("subtitles, captions, closed captions, on-screen text, lyrics on screen, "
            "watermark, logo, timecode, letterboxing, split screen, cartoon, 3d render")

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "out"
OPS = OUT / ".ops"
LOG = threading.Lock()


def say(*a):
    with LOG:
        print(*a, flush=True)


def load_env():
    """Lit veo/.env (CLE=valeur) si le fichier existe. .env est gitignore."""
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def build_prompt(shot, suffix, with_dialogue=True, phonetic=True, alt=None):
    """dialogue_phon = respelling francais pour que le modele prononce juste.
    dialogue = le texte lisible, garde comme reference (et via --raw)."""
    parts = [shot["scene"]]
    line = shot.get("dialogue_phon") if phonetic else None
    line = line or shot.get("dialogue")
    if with_dialogue and line:
        cue = shot.get("cue", "They rap straight to camera")
        parts.append('%s: "%s"' % (cue, line))
    parts.append(alt if (alt and shot.get("style") == "hiphop") else suffix)
    return " ".join(parts)


def load_first_frame(shot):
    """L'API veut un types.Image, pas un File : files.upload() ne marche pas ici."""
    rel = shot.get("first_frame")
    if not rel:
        return None
    path = (ROOT / rel).resolve()
    if not path.exists():
        say("  ! image de reference absente:", path)
        return None
    return types.Image.from_file(location=str(path))


def load_refs(shot):
    """Jusqu'a 3 images de reference. Ignore par lite, qui ne les accepte pas."""
    out = []
    for rel in (shot.get("refs") or [])[:3]:
        path = (ROOT / rel).resolve()
        if path.exists():
            out.append(types.VideoGenerationReferenceImage(
                image=types.Image.from_file(location=str(path)), reference_type="asset"))
        else:
            say("  ! reference absente:", path)
    return out


def videos_of(op):
    resp = getattr(op, "response", None) or getattr(op, "result", None)
    return list(getattr(resp, "generated_videos", None) or []) if resp else []


def refusal_reason(op):
    """Veo renvoie une operation terminee mais vide quand le filtre bloque."""
    resp = getattr(op, "response", None)
    for attr in ("rai_media_filtered_reasons", "raiMediaFilteredReasons"):
        v = getattr(resp, attr, None) if resp else None
        if v:
            return "; ".join(v) if isinstance(v, (list, tuple)) else str(v)
    err = getattr(op, "error", None)
    if err:
        return str(err)
    return None


def poll(client, op, label, timeout=900):
    deadline = time.time() + timeout
    while not op.done:
        if time.time() > deadline:
            raise TimeoutError("%s: pas de reponse apres %ds" % (label, timeout))
        time.sleep(10)
        op = client.operations.get(op)
    return op


def save(client, video, path):
    client.files.download(file=video, destination=str(path))


def run_shot(client, shot, cfg_args, suffix, take):
    sid = shot["id"]
    name = "%s.mp4" % sid if take == 1 else "%s_take%d.mp4" % (sid, take)
    dest = OUT / name
    if dest.exists():
        say("[%s] deja la, on saute (%s)" % (sid, name))
        return "skip"

    opfile = OPS / ("%s.json" % dest.stem)
    image = load_first_frame(shot)
    # allow_adult est refuse en texte seul, allow_all est refuse avec une image.
    person = cfg_args.person_generation
    if person == "auto":
        person = "allow_adult" if image is not None else "allow_all"
    # Gemini Developer API : seed, fps, generate_audio, mask, compression_quality
    # et output_gcs_uri sont refuses (Vertex uniquement).
    refs = load_refs(shot) if cfg_args.model != "lite" else None
    if refs and image is not None:
        image = None  # les deux ensemble ne sont pas acceptes
    config = types.GenerateVideosConfig(
        aspect_ratio="16:9",
        resolution=cfg_args.resolution,
        duration_seconds=str(shot.get("duration", 8)),
        person_generation=person,
        negative_prompt=NEGATIVE if cfg_args.negative else None,
        reference_images=refs or None,
    )

    for attempt, with_dialogue in enumerate([True, False], start=1):
        if not shot.get("dialogue") and attempt == 2:
            break  # rien a retirer, le refus ne vient pas du texte chante
        prompt = build_prompt(shot, suffix, with_dialogue, not cfg_args.raw, cfg_args.suffix_hiphop)

        op = None
        if opfile.exists() and attempt == 1:
            try:
                saved = json.loads(opfile.read_text())
                op = client.operations.get(types.GenerateVideosOperation(name=saved["name"]))
                say("[%s] reprise de l'operation en cours" % sid)
            except Exception:
                op = None

        if op is None:
            say("[%s] envoi%s" % (sid, "" if with_dialogue else " (sans dialogue)"))
            op = client.models.generate_videos(
                model=MODELS[cfg_args.model],
                source=types.GenerateVideosSource(prompt=prompt, image=image),
                config=config,
            )
            OPS.mkdir(parents=True, exist_ok=True)
            opfile.write_text(json.dumps({"name": op.name, "shot": sid}))

        op = poll(client, op, sid, cfg_args.timeout)
        vids = videos_of(op)
        if vids:
            save(client, vids[0].video, dest)
            opfile.unlink(missing_ok=True)
            say("[%s] OK -> %s" % (sid, dest.name))
            return "ok"

        reason = refusal_reason(op) or "refus sans motif renvoye"
        opfile.unlink(missing_ok=True)
        say("[%s] refuse: %s" % (sid, reason))
        if attempt == 1 and shot.get("dialogue"):
            say("[%s] nouvelle tentative sans la ligne chantee" % sid)

    return "fail"


def main():
    # Les prompts sont en francais : sans ca, une console cp1252 fait planter un thread
    # en plein milieu d'une generation deja payee.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", help="ids de plans, ex: 03 07 12")
    ap.add_argument("--take", type=int, default=1, help="numero de prise (>1 = variante)")
    ap.add_argument("--model", default="lite", choices=["lite", "fast", "full"])
    ap.add_argument("--resolution", default="1080p", choices=["720p", "1080p", "4k"])
    ap.add_argument("--person-generation", default="auto",
                    choices=["auto", "allow_adult", "allow_all"],
                    help="auto = allow_adult avec image, allow_all en texte seul")
    ap.add_argument("--raw", action="store_true",
                    help="utilise le texte original au lieu du respelling phonetique")
    ap.add_argument("--negative", action="store_true",
                    help="envoie un negative_prompt (refuse par lite, ok en 3.1 / 3.1-fast)")
    ap.add_argument("--workers", type=int, default=3, help="generations en parallele")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.loads((ROOT / "prompts.json").read_text(encoding="utf-8"))
    suffix = data["suffix"]
    args.suffix_hiphop = data.get("suffix_hiphop")
    shots = data["shots"]
    if args.only:
        wanted = set(args.only)
        shots = [s for s in shots if s["id"] in wanted]
        missing = wanted - {s["id"] for s in shots}
        if missing:
            sys.exit("ids inconnus: %s" % ", ".join(sorted(missing)))

    grille = PRICE_PER_SEC[args.model]
    if args.resolution not in grille:
        sys.exit("%s ne fait pas de %s." % (args.model, args.resolution))
    secs = sum(s.get("duration", 8) for s in shots)
    cost = secs * grille[args.resolution]
    say("%d plans, %d s, %s %s -> ~%.2f USD la passe"
        % (len(shots), secs, args.model, args.resolution, cost))

    huit = [s["id"] for s in shots if s.get("duration", 8) == 8]
    if huit and args.model == "lite" and args.resolution == "720p":
        say("! lite: 8 s exige 1080p. %d plans vont echouer." % len(huit))
    if args.resolution == "4k":
        court = [s["id"] for s in shots if s.get("duration", 8) != 8]
        if court:
            sys.exit("4K impose 8 s. Plans hors format: %s" % ", ".join(court))
        avec_img = [s["id"] for s in shots if s.get("first_frame") or s.get("refs")]
        if avec_img:
            say("! 4K + image d'entree non confirme par la doc. Plans concernes: %s"
                % ", ".join(avec_img))
    if args.negative and args.model == "lite":
        sys.exit("lite refuse negative_prompt (400). Retire --negative ou passe en fast.")

    if args.dry_run:
        for s in shots:
            say("\n--- %s (%s, %ds)" % (s["id"], s["tc"], s.get("duration", 8)))
            if s.get("first_frame"):
                say("    premiere image:", s["first_frame"])
            say(build_prompt(s, suffix, True, not args.raw, args.suffix_hiphop))
        return

    load_env()
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        sys.exit("GEMINI_API_KEY absente. Pose-la dans veo/.env ou via setx, puis relance.")

    OUT.mkdir(parents=True, exist_ok=True)
    client = genai.Client()

    tally = {"ok": 0, "skip": 0, "fail": 0}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_shot, client, s, args, suffix, args.take): s for s in shots}
        for f in as_completed(futures):
            sid = futures[f]["id"]
            try:
                tally[f.result()] += 1
            except Exception as e:
                tally["fail"] += 1
                say("[%s] erreur: %s" % (sid, e))

    say("\ngeneres %d | sautes %d | echecs %d" % (tally["ok"], tally["skip"], tally["fail"]))
    if tally["fail"]:
        say("relance la commande: les plans reussis sont sautes automatiquement.")


if __name__ == "__main__":
    main()
