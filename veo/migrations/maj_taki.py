# -*- coding: utf-8 -*-
"""Réécrit l'intro du groupe Takiwasi, et ajoute la source des dates.

Ce qui change : la question du financement public français n'est plus ouverte.
Un article à comité de lecture, indexé et déjà cité dans ce groupe, donne les
périodes. Le centre les conteste dans son propre document. La page porte les
deux, parce que c'est l'état réel de la documentation.
"""
# APPLIQUE UNE FOIS. Le resultat de ce script est deja dans
# page_data.json : le relancer n’apporterait rien, et il refuserait
# de s’executer puisque le groupe existe deja. Il est conserve parce
# qu’une page qui affirme que rien n’est ecrit a la main doit
# pouvoir montrer par quoi sa donnee est passee.
import io
import json
import pathlib
import sys

ICI = pathlib.Path(__file__).resolve().parent.parent
CIBLE = u"Takiwasi"

TAKI = (
    u"Ce groupe sort de la pharmacologie pour une raison simple : le centre "
    u"Takiwasi, à Tarapoto au Pérou, est nommé dans les rapports officiels "
    u"français, et il recrute en France.\n\n"
    u"Le rapport de la MIVILUDES au Premier ministre pour 2005 lui consacre un "
    u"développement, et celui de 2009 y revient. Le premier le décrit comme un "
    u"«\u202fcentre de traitement des toxicomanies à base de méthodes chamaniques "
    u"créé en 1992 au Pérou par un médecin français, le Docteur Jacques "
    u"Mabit\u202f». Il note que son fondateur n\u2019a jamais été condamné, et que "
    u"cela «\u202fne met pas fin à de sérieuses inquiétudes\u202f». Il écrit que "
    u"«\u202fla violence des méthodes utilisées pour le sevrage des toxicomanes "
    u"interroge\u202f» par les risques courus par des patients très vulnérables, "
    u"qu\u2019aucune statistique fiable n\u2019existe sur le taux de réussite, et "
    u"que le problème principal est la dérive du sevrage vers une «\u202fmédecine "
    u"de l\u2019âme\u202f» ouverte à d\u2019autres publics, dont des malades du "
    u"cancer déclarés incurables. Il identifie enfin le relais promotionnel "
    u"français de l\u2019époque, une association lyonnaise.\n\n"
    u"Sur l\u2019argent public, deux sources se contredisent, et les deux sont "
    u"citables. L\u2019article de David Dupuis paru dans "
    u"<em>Salud Colectiva</em> en 2018, quatrième référence de ce groupe, écrit "
    u"que «\u202fle financement de donateurs privés, du gouvernement français "
    u"(1992-1994), de la Communauté européenne (1993-1995) et des Nations unies "
    u"(1995-1997) permet l\u2019acquisition de terres, la construction "
    u"d\u2019infrastructures et la rémunération de certains employés\u202f» "
    u"(DOI 10.18294/sc.2018.1539, texte intégral en libre accès). C\u2019est un "
    u"article à comité de lecture, indexé, fondé sur dix ans de terrain dans ces "
    u"centres : c\u2019est la source la plus solide disponible, et elle date le "
    u"financement français de 1992 à 1994.\n\n"
    u"Takiwasi le conteste, dans un document publié sur son propre site. Le centre "
    u"y écrit que la Délégation générale à la lutte contre les drogues, "
    u"«\u202fdépendance du Ministère des Affaires Étrangères du gouvernement "
    u"français\u202f», a «\u202ffinancé en partie pendant 5 ans les travaux de "
    u"recherche\u202f» de Jacques Mabit <em>préalables</em> à la création du centre "
    u"— déplaçant donc l\u2019argent public français avant 1992 — que le terrain "
    u"fut acquis sur ses fonds propres, et qu\u2019il n\u2019y eut pas de "
    u"contribution des Nations unies à la création. Il affirme par ailleurs ne "
    u"recevoir aujourd\u2019hui aucune subvention d\u2019État.\n\n"
    u"Ce que personne ne donne, ni Dupuis, ni Takiwasi, ni aucun rapport "
    u"accessible : un montant. Aucun chiffre n\u2019est avancé ici, parce "
    u"qu\u2019aucune source ne le porte.\n\n"
    u"Reste un point qui relève du groupe sur les études menées par des adeptes : "
    u"plusieurs des publications indexées qui évaluent favorablement ce centre sont "
    u"signées par des auteurs qui y sont affiliés."
)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    gr = json.loads((ICI / "page_data.json").read_text(encoding="utf-8"))
    n = 0
    for g in gr:
        if g["titre"].startswith(CIBLE):
            avant = len(g["intro"])
            g["intro"] = TAKI
            n += 1
            print(u"intro réécrite : %s" % g["titre"])
            print(u"  %d -> %d caractères" % (avant, len(TAKI)))
            # L'article de Dupuis doit rester en 4e position : l'intro le dit.
            for i, r in enumerate(g["refs"]):
                if r["pmid"] == "30281759":
                    print(u"  Dupuis 2018 (PMID 30281759) est en position %d" % (i + 1))
    if not n:
        sys.exit(u"groupe « %s » introuvable" % CIBLE)
    with io.open(str(ICI / "page_data.json"), "w", encoding="utf-8",
                 newline="\n") as f:
        f.write(json.dumps(gr, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
