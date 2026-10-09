#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Televerse les sous-titres multilingues de TOXICOSQUEROS sur YouTube.

    .venv/Scripts/python.exe youtube_srt.py VIDEO_ID           # montre le plan, n'ecrit rien
    .venv/Scripts/python.exe youtube_srt.py VIDEO_ID --go      # televerse pour de bon
    .venv/Scripts/python.exe youtube_srt.py VIDEO_ID --go en es  # seulement ces langues
    .venv/Scripts/python.exe youtube_srt.py VIDEO_ID --etat    # liste ce qui est deja en ligne

SANS --go, LE SCRIPT N'ECRIT RIEN. Il lit la video, compare avec les fichiers locaux,
et affiche ce qu'il ferait. C'est le mode par defaut, volontairement.

Rejouable : une piste qui existe deja dans une langue est MISE A JOUR, pas dupliquee.
On peut donc relancer apres avoir corrige une traduction.

--------------------------------------------------------------------------------
CE QU'IL FAUT FAIRE UNE FOIS, ET QUE PERSONNE D'AUTRE QUE TOI NE PEUT FAIRE
--------------------------------------------------------------------------------
Televerser des sous-titres n'est pas possible avec une simple cle API : il faut une
autorisation OAuth, c'est-a-dire que tu dises toi-meme a Google, dans ton navigateur,
que ce programme a le droit d'ecrire sur TA chaine.

1. console.cloud.google.com  ->  cree un projet (ou reprends celui de Veo).
2. "API et services" -> "Bibliotheque" -> active YouTube Data API v3.
3. "Ecran de consentement OAuth" -> type "Externe" -> renseigne le minimum ->
   dans "Utilisateurs test", AJOUTE TON PROPRE COMPTE GOOGLE.
   Sans cette ligne, l'autorisation sera refusee avec "access_denied".
4. "Identifiants" -> "Creer des identifiants" -> "ID client OAuth" ->
   type d'application : "Application de bureau".
5. Telecharge le JSON et depose-le ici sous le nom  client_secret.json
   (il est deja dans .gitignore, il ne partira nulle part).

A la premiere execution avec --go, un navigateur s'ouvre : tu te connectes a Google
et tu acceptes. Le jeton est ensuite garde dans .youtube_token.json et les fois
suivantes sont silencieuses.

Ton mot de passe Google ne transite jamais par ce script : la connexion se fait
dans ton navigateur, sur les pages de Google, et le script ne recoit qu'un jeton.
--------------------------------------------------------------------------------
"""
import io
import os
import pathlib
import re
import sys

ICI = pathlib.Path(__file__).resolve().parent
SRT = ICI.parent                       # les .srt sont a cote du montage
SECRET = ICI / "client_secret.json"
JETON = ICI / ".youtube_token.json"

# Ecrire sur les sous-titres d'une chaine exige cette portee, et pas une moindre.
PORTEES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Code du fichier local -> code de langue declare a YouTube (BCP-47).
# "pt" vaut "pt-BR" parce que pt.json annonce lui-meme « portugues (Brasil) », et que
# c'est au Bresil que cette piste sera le plus lue. Declarer "pt" afficherait
# « portugais » tout court et perdrait cette precision.
LANGUES = {
    "fr": "fr", "en": "en", "es": "es", "pt": "pt-BR", "de": "de",
    "it": "it", "nl": "nl", "ru": "ru", "uk": "uk",
}

# snippet.name est OBLIGATOIRE et ne doit pas etre vide. Surtout : le couple
# (language, name) est la cle d'unicite d'une piste. Changer un seul de ces
# libelles entre deux executions ne met pas la piste a jour, il en cree une
# seconde a cote. Ils sont donc ecrits en dur ici, et ne doivent jamais etre
# derives d'une variable, d'un nom de fichier ou d'une traduction.
NOMS = {
    "fr": "Francais", "en": "English", "es": "Espanol", "pt": "Portugues (Brasil)",
    "de": "Deutsch", "it": "Italiano", "nl": "Nederlands",
    "ru": "Russkiy", "uk": "Ukrainska",
}

# Cout en unites de quota. Quota journalier par defaut : 10 000 unites.
# Les requetes EN ECHEC sont facturees elles aussi.
# Le compteur se remet a zero a minuit heure du Pacifique, soit 9 h ou 10 h
# en France selon la saison : epuiser son quota le soir bloque jusqu'au matin.
#
# Budget reel : neuf creations = 3 600. Une relance complete = 50 + 9 x 450 = 4 100.
# Un premier passage suivi d'une relance consomme 7 700 : il ne reste pas de quoi
# en faire une troisieme dans la journee. Mieux vaut verifier les fichiers avant
# d'envoyer qu'apres.
COUT = {"list": 50, "insert": 400, "update": 450, "delete": 50, "download": 200}

BLOC = re.compile(
    r"^(\d+)\s*\n"
    r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})[^\n]*\n"
    r"((?:.+\n?)+)", re.M)


def secondes(h):
    hh, mm, reste = h.split(":")
    ss, ms = reste.split(",")
    return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000.0


def verifier(chemin):
    """Relit un SRT avant de le televerser. Un fichier refuse coute du quota pour rien."""
    brut = chemin.read_bytes()
    ennuis = []
    if brut.startswith(b"\xef\xbb\xbf"):
        ennuis.append("BOM UTF-8 en tete")
    try:
        texte = brut.decode("utf-8")
    except UnicodeDecodeError as e:
        return None, ["pas de l'UTF-8 valide : %s" % e]
    blocs = BLOC.findall(texte.replace("\r\n", "\n"))
    if not blocs:
        return None, ["aucun bloc reconnu : ce n'est pas du SubRip"]
    n = [int(b[0]) for b in blocs]
    if n != list(range(1, len(n) + 1)):
        ennuis.append("numerotation non continue")
    fin = 0.0
    for b in blocs:
        d, f = secondes(b[1]), secondes(b[2])
        if f <= d:
            ennuis.append("bloc %s : fin avant debut" % b[0])
        if d < fin - 0.001:
            ennuis.append("bloc %s : chevauche le precedent" % b[0])
        fin = max(fin, f)
    return {"blocs": len(blocs), "fin": fin, "octets": len(brut)}, ennuis


def fichiers(voulues):
    trouves = []
    for code in sorted(LANGUES):
        if voulues and code not in voulues:
            continue
        p = SRT / ("TOXICOSQUEROS.%s.srt" % code)
        if p.exists():
            trouves.append((code, p))
    return trouves


def service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    cred = None
    if JETON.exists():
        cred = Credentials.from_authorized_user_file(str(JETON), PORTEES)
    if cred and cred.expired and cred.refresh_token:
        try:
            cred.refresh(Request())
        except Exception as e:
            print("  jeton perime et non rafraichissable (%s), reconnexion" % e)
            cred = None
    if not cred or not cred.valid:
        if not SECRET.exists():
            sys.exit("Il manque %s. Voir l'en-tete de ce fichier, etapes 1 a 5." % SECRET.name)
        print("  ouverture du navigateur : connecte-toi a Google et accepte.")
        cred = InstalledAppFlow.from_client_secrets_file(
            str(SECRET), PORTEES).run_local_server(port=0)
        JETON.write_text(cred.to_json(), encoding="utf-8")
        try:
            os.chmod(str(JETON), 0o600)
        except Exception:
            pass
        print("  jeton enregistre dans %s" % JETON.name)
    return build("youtube", "v3", credentials=cred, cache_discovery=False)


def en_ligne(yt, video):
    """Pistes deja attachees a la video, indexees par code de langue."""
    r = yt.captions().list(part="snippet", videoId=video).execute()
    pistes = {}
    for it in r.get("items", []):
        s = it["snippet"]
        pistes.setdefault(s["language"], []).append({
            "id": it["id"], "nom": s.get("name", ""),
            "piste": s.get("trackKind", ""), "brouillon": s.get("isDraft", False),
            "maj": s.get("lastUpdated", ""),
        })
    return pistes


def televerser(yt, video, code, chemin, existant, nom):
    from googleapiclient.http import MediaFileUpload
    # mimetype explicite : Python ne connait pas .srt, l'omettre leve UnknownFileType.
    media = MediaFileUpload(str(chemin), mimetype="application/octet-stream",
                            chunksize=-1, resumable=True)
    if existant:
        rep = yt.captions().update(
            part="snippet",
            body={"id": existant["id"], "snippet": {"isDraft": False}},
            media_body=media).execute()
        return "mise a jour", rep["id"]
    rep = yt.captions().insert(
        part="snippet",
        body={"snippet": {"videoId": video, "language": LANGUES[code],
                          "name": nom, "isDraft": False}},
        media_body=media).execute()
    return "creation", rep["id"]


def main():
    args = [a for a in sys.argv[1:]]
    go = "--go" in args
    etat_seul = "--etat" in args
    args = [a for a in args if not a.startswith("--")]
    if not args:
        sys.exit(__doc__.strip().split("\n\n")[1])
    video = args[0]
    voulues = set(args[1:])

    locaux = fichiers(voulues)
    if not locaux:
        sys.exit("aucun TOXICOSQUEROS.<langue>.srt trouve dans %s" % SRT)

    print("TOXICOSQUEROS - sous-titres YouTube")
    print("video : %s" % video)
    print("\n== fichiers locaux")
    valides = []
    for code, p in locaux:
        info, ennuis = verifier(p)
        if info is None:
            print("  %-3s REFUSE  %s" % (code, " ; ".join(ennuis)))
            continue
        marque = "  " if not ennuis else " !"
        print("  %-3s %3d blocs  jusqu'a %6.2f s  %5.1f ko%s%s"
              % (code, info["blocs"], info["fin"], info["octets"] / 1024.0,
                 marque, " ; ".join(ennuis)))
        valides.append((code, p))
    if not valides:
        sys.exit("\nAucun fichier valide. Rien n'a ete envoye.")

    print("\n== connexion")
    yt = service()
    pistes = en_ligne(yt, video)
    depense = COUT["list"]

    print("\n== deja en ligne")
    if not pistes:
        print("  aucune piste de sous-titres sur cette video")
    for lang in sorted(pistes):
        for t in pistes[lang]:
            print("  %-6s %s  %s%s  maj %s"
                  % (lang, t["id"], t["piste"],
                     "  BROUILLON" if t["brouillon"] else "", t["maj"][:10]))

    print("\n== plan")
    travaux, cout = [], depense
    for code, p in valides:
        cible = LANGUES[code]
        deja = pistes.get(cible)
        # On ne touche qu'aux pistes televersees, jamais a une transcription automatique.
        propre = next((t for t in (deja or []) if t["piste"] != "ASR"), None)
        acte = "mise a jour" if propre else "creation"
        cout += COUT["update" if propre else "insert"]
        travaux.append((code, p, propre))
        print("  %-3s -> %-6s %s%s"
              % (code, cible, acte, "  (%s)" % propre["id"] if propre else ""))
    print("\n  cout estime : %d unites de quota sur les 10 000 par jour" % cout)

    if etat_seul:
        return
    if not go:
        print("\nRien n'a ete envoye. Relance avec --go pour televerser.")
        return

    print("\n== televersement")
    # Les erreurs les plus frequentes, traduites. Un 403 SERVICE_DISABLED ne
    # ressemble pas a un probleme d'autorisation et fait perdre une heure :
    # c'est l'API YouTube Data v3 qui n'a pas ete activee dans le projet Cloud.
    EXPLIQUE = {
        "captionExists": u"une piste existe deja pour ce couple langue + nom ; "
                         u"le nom a change depuis la derniere fois",
        "invalidMetadata": u"langue, nom ou identifiant de video invalide",
        "nameTooLong": u"le nom de piste depasse 150 caracteres",
        "videoNotFound": u"identifiant de video introuvable : as-tu colle l'URL "
                         u"complete au lieu de l'identifiant seul ?",
        "contentRequired": u"le fichier n'est pas arrive",
        "SERVICE_DISABLED": u"l'API YouTube Data v3 n'est pas activee dans le projet "
                            u"Google Cloud. Bibliotheque > YouTube Data API v3 > Activer",
        "quotaExceeded": u"quota epuise. Il repart a minuit heure du Pacifique, "
                         u"soit 9 h ou 10 h en France",
    }
    for code, p, propre in travaux:
        try:
            acte, cid = televerser(yt, video, code, p, propre, NOMS.get(code, ""))
            print("  %-3s %-12s %s" % (code, acte, cid))
        except Exception as e:
            msg = str(e)
            raison = next((v for k, v in EXPLIQUE.items() if k in msg), None)
            print("  %-3s ECHEC  %s" % (code, raison or msg[:160]))
            if raison:
                print("        (%s)" % msg[:120])
    print("\nVerifie dans YouTube Studio > Sous-titres.")
    print("Relance sans --go a tout moment : le script montre l'etat sans rien ecrire.")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()
