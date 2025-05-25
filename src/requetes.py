"""
Fonctions pour le traitement des requêtes.
"""

import string
import re
from datetime import datetime
from typing import Tuple, List, Dict, Optional


def nettoyage_requete(requete: str) -> str:
    """
    Corrige les requêtes en supprimant les 'stop words' (par rapport aux requêtes du TD)
    et les ponctuations.
    :param requete: La requête à corriger.
    :return: La requête corrigée
    """
    # Normalisation apostrophes
    requete = requete.replace("’", "'")
    requete = requete.replace("'", " ' ")

    with open("data/stop_words_requetes.txt", "r", encoding="utf-8") as f:
        liste_stop_words = [ligne.strip() for ligne in f]

    requete = requete.lower()
    liste_mots = [mot for mot in requete.split() if mot not in liste_stop_words]

    requete_propre = " ".join(liste_mots)
    punct = string.punctuation
    for c in punct:
        if c != "-":
            requete_propre = requete_propre.replace(c, "")

    return requete_propre


def extract_doctype(requete: str) -> Tuple[str, str]:
    """
    Extrait un type de document à retourner (article, bulletin ou rubrique)
    étant donné une requête.
    On considère qu'il se trouve en première position dans le texte
    passé en paramètre.
    Par défaut, la fonction renvoie "article".
    :param requete: La requête à analyser.
    :return: Un tuple (type, requête sans le type)
    """
    liste_texte = requete.lower().split()
    doc_type = liste_texte[0]
    if doc_type not in ["article", "bulletin", "rubrique"]:
        if doc_type == "articles":
            liste_texte.remove(doc_type)
            doc_type = "article"
        elif doc_type == "bulletins":
            liste_texte.remove(doc_type)
            doc_type = "bulletin"
        elif doc_type == "rubriques":
            liste_texte.remove(doc_type)
            doc_type = "rubrique"
        else:
            doc_type = "article"
    else:
        liste_texte.remove(doc_type)
    texte_propre = " ".join(liste_texte)

    return doc_type, texte_propre


def extract_rubriques(requete: str) -> Tuple[List[str], str]:
    """
    Extrait la ou les rubriques demandées dans une requête.
    :param requete: La requête à analyser.
    :return: Un tuple (rubrique, requête sans la rubrique)
    """
    # Le texte est sans stop-words à ce stade,
    # il faut donc lister les rubriques sans stop-words
    # (et certaines avec possiblement des fautes).
    liste_rubriques = [
        "focus",
        "au coeur regions",
        "evenement",
        "événement",
        "evénement",
        "évènement",
        "direct laboratoires",
        "direct labos",
        "a lire",
        "horizon enseignement",
        "horizons enseignement",
        "horizons formation enseignement",
        "horizon formation",
        "actualités innovations",
        "actualités innovation",
        "actualité innovation",
        "côté pôles",
    ]

    rubriques = []
    texte = requete.lower()

    # Remplacer tous les " ou " entre les rubriques par juste un espace
    # (on prépare la regex avant de supprimer les rubriques)
    rubrique_pattern = "|".join(re.escape(r) for r in liste_rubriques)
    # Cas : rubrique1 ou rubrique2
    texte = re.sub(
        rf"({rubrique_pattern})\s+ou\s+({rubrique_pattern})", r"\1 \2", texte
    )

    for rubrique in liste_rubriques:
        if rubrique in texte:
            rubriques.append(rubrique)
            texte = texte.replace(rubrique, "")

    # Nettoyage des espaces
    requete_propre = re.sub(r"\s+", " ", texte).strip()

    return rubriques, requete_propre


def extract_keywords(requete: str) -> List[str]:
    """
    Extrait les mots-clés d'une requête (à supposer qu'elle ne contienne plus de dates,
    de rubriques, etc.)
    :param requete: La requête à analyser.
    :return: Une liste de mots-clés.
    """
    keywords = []

    # 2. Séparer les mots avec apostrophes comme d'ingénieurs → d ingénieurs
    requete = re.sub(r"\b(d|l|qu|n|s|c|j|t)'", r"\1 ", requete, flags=re.IGNORECASE)
    print(requete)

    mots = re.findall(r"\b\w+(?:-\w+)*\b", requete)
    stopwords_apres_pas = {"de", "du", "des", "d", "la", "le", "les", "l"}

    i = 0
    while i < len(mots):
        if mots[i].lower() == "pas":
            j = i + 1
            # Sauter les petits mots inutiles entre "pas" et le mot-clé
            while j < len(mots) and mots[j].lower() in stopwords_apres_pas:
                j += 1
            if j < len(mots):
                keywords.append("pas " + mots[j])
                i = j + 1
            else:
                i += 1
        else:
            keywords.append(mots[i])
            i += 1

    return keywords


def extract_titre(requete: str) -> Tuple[Optional[str], str]:
    """
    Extrait une chaîne de caractère si le titre est mentionné
    dans la requête.
    :param requete: La requête à analyser.
    :return: Un tuple (titre, requête sans titre)
    """
    titre = None

    # Cas "titre" + contenu entre « » ou " " ou ' '
    m = re.search(r'\btitre\s+(["«\'])(.+?)["»\']', requete)
    if m:
        titre = m.group(2)
        # Supprimer 'titre «...», titre "...", titre '...'
        pattern = (
            r"\btitre\s+["
            + re.escape(m.group(1))
            + r"]"
            + re.escape(titre)
            + r"["
            + ("»" if m.group(1) == "«" else re.escape(m.group(1)))
            + r"]"
        )
        requete = re.sub(pattern, "", requete, count=1)
    else:
        # Cas "titre" + <mot>
        m = re.search(r"\btitre\s+(\S+)", requete)
        if m:
            titre_candidat = m.group(1)
            titre = titre_candidat
            requete = re.sub(
                r"\btitre\s+" + re.escape(titre_candidat), "", requete, count=1
            )

    # Cas <mot> + "titre" (si titre est en dernier)
    if not titre:
        m = re.search(r"\b(\w+)\s+titre\b", requete)
        if m:
            titre = m.group(1)
            requete = re.sub(
                r"\b" + re.escape(titre) + r"\s+titre\b", "", requete, count=1
            )

    requete_propre = re.sub(r"\s+", " ", requete).strip()

    return titre, requete_propre


def extract_contenu(requete: str) -> Tuple[Optional[str], str]:
    """
    Extrait un mot en lien avec le contenu si le mot "contenu"
    est présent explicitement dans la requête.
    :param requete: La requête à analyser.
    :return: Un tuple (contenu, requete sans contenu)
    """
    contenu = None
    # Chercher "contenu" + <mot>
    m = re.search(r"\bcontenu\s+(\S+)", requete)
    if m:
        contenu = m.group(1)
        # Supprimer "contenu <mot>" du texte
        requete = re.sub(r"\bcontenu\s+" + re.escape(contenu), "", requete, count=1)

    requete_propre = re.sub(r"\s+", " ", requete).strip()
    return contenu, requete_propre


MOIS_FR = {
    "janvier": "01",
    "février": "02",
    "fevrier": "02",
    "mars": "03",
    "avril": "04",
    "mai": "05",
    "juin": "06",
    "juillet": "07",
    "août": "08",
    "aout": "08",
    "septembre": "09",
    "octobre": "10",
    "novembre": "11",
    "décembre": "12",
    "decembre": "12",
}


def parse_date_str(date_texte: str) -> Optional[str]:
    """
    Renvoie un pattern de date étant donné une chaîne de caractères.
    :param date_texte: Le texte contenant la date.
    :return: Une version formatée de la date (YYYY-MM-DD).
    """
    date_texte = date_texte.strip()
    m = re.match(r"(\d{1,2})\s+([a-zéèêç]+)\s+(\d{4})", date_texte)
    if m:
        jour, mois, annee = m.groups()
        if mois in MOIS_FR:
            return f"{annee}-{MOIS_FR[mois]}-{int(jour):02d}"
    m = re.match(r"([a-zéèêç]+)\s+(\d{4})", date_texte)
    if m:
        mois, annee = m.groups()
        if mois in MOIS_FR:
            return f"{annee}-{MOIS_FR[mois]}-**"
    m = re.match(r"(\d{8})", date_texte)
    if m:
        try:
            d = datetime.strptime(m.group(1), "%d%m%Y")
            return d.strftime("%Y-%m-%d")
        except ValueError:
            return None
    m = re.match(r"(19|20)\d{2}", date_texte)
    if m:
        return f"{m.group(0)}-**-**"
    return None


def requete_sans_dates(requete: str) -> str:
    """
    Supprime d'une requête toutes les informations de date.
    :param requete: La requête à nettoyer.
    :return: LA requête nettoyée.
    """
    mois_pattern = "|".join(
        [
            "janvier",
            "février",
            "fevrier",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "août",
            "aout",
            "septembre",
            "octobre",
            "novembre",
            "décembre",
            "decembre",
        ]
    )
    requete = re.sub(r"\b\d{1,2}\s+(" + mois_pattern + r")\s+\d{4}\b", "", requete)
    requete = re.sub(r"\b(" + mois_pattern + r")\s+\d{4}\b", "", requete)
    requete = re.sub(
        r"\b(au mois de|au mois|en|de|du|dans)\s+(" + mois_pattern + r")\b",
        "",
        requete,
    )
    requete = re.sub(r"\b(19|20)\d{2}\b", "", requete)
    requete = re.sub(r"\b\d{8}\b", "", requete)  # important pour enlever 14062013 etc.
    requete = re.sub(
        r"\b(entre|et|avant|après|apres|d’après|d\'apres|année|depuis|pas au mois de|au mois|mois|à partir)\b",
        "",
        requete,
    )
    requete = re.sub(r"\s+", " ", requete)
    return requete.strip()


def extract_date_info(requete: str) -> Tuple[Dict[str, str] | None, str]:
    """
    Extrait toutes les informations de dates dans une requête pour les convertir
    en un format standard.
    :param requete: La requête à analyser.
    :return: Un tuple (dates, requête sans les dates)
    """
    texte_original = requete
    requete = requete.lower()

    resultat = {}

    # Cas 0 : exclusion avec "pas"
    m = re.search(
        r"pas\s+(au mois de|au mois|en|de|du)?\s*([a-zéèêç]+)(?:[\s,\.]|$)", requete
    )
    if m:
        mot = m.group(2)
        if mot in MOIS_FR:
            resultat["pas"] = f"****-{MOIS_FR[mot]}-**"

    # Cas avec des préfixes temporels
    patterns = [
        (
            r"entre\s+(.*?)\s+et\s+(.*)",
            lambda m: {
                "min": parse_date_str(m.group(1)),
                "max": parse_date_str(m.group(2)),
            },
        ),
        (
            r"(à partir de|à partir|après|apres|d’après|d\'apres|depuis)\s+([^\.,;]*)",
            lambda m: {"min": parse_date_str(m.group(2))},
        ),
        (r"avant\s+(.+?)(?:[\s,\.]|$)", lambda m: {"max": parse_date_str(m.group(1))}),
        (
            r"(en|de|du|dans|au mois de|au mois)\s+(.+?)(?:[\s,\.]|$)",
            lambda m: {"exact": parse_date_str(m.group(2))},
        ),
    ]

    for pattern, fonction in patterns:
        m = re.search(pattern, requete)
        if m:
            result = fonction(m)
            if any(result.values()):
                resultat.update({k: v for k, v in result.items() if v})
                return resultat, requete_sans_dates(texte_original)

    mots = requete.split()

    # Cas 5 et 6 : sliding window
    for window in [3, 2]:
        for i in range(len(mots) - window + 1):
            segment = " ".join(mots[i : i + window])
            d = parse_date_str(segment)
            if d:
                resultat["exact"] = d
                return resultat, requete_sans_dates(texte_original)

    # Cas 7 : année seule
    for mot in mots:
        d = parse_date_str(mot)
        if d:
            resultat["exact"] = d
            return resultat, requete_sans_dates(texte_original)

    return resultat if resultat else None, requete_sans_dates(texte_original)


def extract_image(requete: str) -> Tuple[None | int, str]:
    """
    Extrait la demande d'image à partir d'une requête.
    :param requete: La requête à analyser.
    :return: Un tuple (image (oui, non ou None), requête sans images)
    """
    if "images" in requete:
        if "sans images" in requete:
            requete = requete.replace("sans images", "")
            return 0, requete
        requete = requete.replace("images", "")
        return 1, requete
    if "image" in requete:
        if "sans image" in requete:
            requete = requete.replace("sans image", "")
            return 0, requete
        requete = requete.replace("image", "")
        return 1, requete

    return None, requete


def replace_soit(requete: str) -> str:
    """
    Remplace la structure "soit...soit" par des "ou" pour simplifier le traitement.
    :param requete: La requête à traiter.
    :return: La nouvelle requête.
    """
    compteur_soit = 0
    for mot in requete.split():
        if mot == "soit":
            compteur_soit += 1
    if compteur_soit >= 2:
        requete = requete.replace("soit", "", 1)
        requete = requete.replace("soit", "ou")

    return requete


def traitement_requete(requete_langage_naturel):
    """
    Traite une requête en langage naturel pour extraire des informations structurées.

    :param requete_langage_naturel: La requête en langage naturel saisie par l'utilisateur,
    contenant des informations sur les critères de recherche dans l'archive ADIT.
    :return: Un dictionnaire contenant les éléments extraits de la requête, incluant :
        - 'query' : La requête en langage naturel.
        - 'date' : Les informations de date extraites de la requête (peut être vide).
        - 'titre' : Le titre extrait, s'il y en a un.
        - 'contenu' : Le contenu si mentionné.
        - 'keywords' : Liste des mots-clés extraits de la requête.
        - 'rubriques' : Liste des rubriques extraites.
        - 'doc_type' : Le type de document à extraire (ex : article, bulletin).
        - 'image' : Les informations relatives à une image, si mentionnées.
    """

    doc_type, texte_liste = extract_doctype(requete_langage_naturel)

    # Enlever les rubriques article ou bulletin à l'intérieur du texte
    texte_liste = texte_liste.split()
    mots_inutiles = [
        "article",
        "articles",
        "bulletin",
        "bulletins",
        "rubrique",
        "rubriques",
    ]

    texte_liste = " ".join([word for word in texte_liste if word not in mots_inutiles])

    # rubriques
    rubriques, texte_liste = extract_rubriques(texte_liste)

    # dates
    date, texte_liste = extract_date_info(texte_liste)

    # titre
    titre, texte_liste = extract_titre(texte_liste)

    # contenu
    contenu, texte_liste = extract_contenu(texte_liste)

    # image
    image, texte_liste = extract_image(texte_liste)

    # mots-clés (ceux qui reste : on recherchera dans titre +texte)
    keywords = extract_keywords(texte_liste)

    # structure de la requête
    requete_structure = {
        "query": requete_langage_naturel,
        "date": date,
        "titre": titre,
        "contenu": contenu,
        "keywords": keywords,
        "rubriques": rubriques,
        "doc_type": doc_type,
        "image": image,
    }

    return requete_structure
