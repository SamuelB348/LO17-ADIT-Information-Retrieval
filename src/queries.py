"""
Fonctions pour le traitement des requêtes.
"""

import string
import re
from datetime import datetime
from typing import Tuple, List


def clean_query(query: str) -> str:
    """
    Corrige les requêtes en supprimant les 'stop words' (par rapport aux requêtes du TD)
    et les ponctuations.
    :param query: La requête à corriger.
    :return: La requête corrigée
    """
    liste_stop_words = [
        "je",
        "non",
        "mentionnent",
        "propos",
        "fois",
        "d",
        "terme",
        "cité",
        "parus",
        "avec",
        "date",
        "est-il",
        "le",
        "évoque",
        "voudrais",
        "impliquant",
        "portant",
        "traite",
        "évoquent",
        "publiés",
        "évoquant",
        "datent",
        "qui",
        "contenant",
        "datés",
        "provenant",
        "possédant",
        "en",
        "mot",
        "contennant",
        "concernent",
        "traitant",
        "contiennent",
        "mentionnant",
        "contient",
        "que",
        "est",
        "ne",
        "mais",
        "parlent",
        "parlant",
        "possédant",
        "portent",
        "porte",
        "liés",
        "de",
        "trouve-t-on",
        "ont",
        "pour",
        "à propos",
        "du",
        "dont",
        "quels",
        "donc",
        "avoir",
        "sont",
        "la",
        "un",
        "liste",
        "projet",
        "les",
        "afficher",
        "obtenir",
        "voir",
        "veux",
        "donner",
        "chercher",
        "nous",
        "souhaitons",
        "des",
        "souhaite",
        "cherche",
        "rechercher",
        "recherches",
        "écrits",
        "j’aimerais",
        "dans",
        "quelles",
        "tout",
        "tous",
        "l",
        "souhaites",
        "mots",
        "lister",
        "trouver",
        "quelle",
        "listez-moi",
        "retournez",
        "retourner",
        "d’",
        "parle",
        "sur",
    ]
    query = query.lower()
    list_words = query.split()
    list_words_copy = list_words.copy()
    for mot in list_words_copy:
        if mot in liste_stop_words:
            list_words.remove(mot)

    cleaned_query = " ".join(list_words)
    punct = string.punctuation
    for c in punct:
        if c != "-":
            cleaned_query = cleaned_query.replace(c, "")

    return cleaned_query


def extract_doctype(query: str) -> Tuple[str, str]:
    """
    Extrait un type de document à retourner (article, bulletin ou rubrique)
    étant donné une requête.
    On considère qu'il se trouve en première position dans le texte
    passé en paramètre.
    Par défaut, la fonction renvoie "article".
    :param query: La requête à analyser.
    :return: Un tuple (type, requête sans le type)
    """
    query = query.lower()
    list_text = query.split()
    doc_type = list_text[0]
    if doc_type not in ["article", "bulletin", "rubrique"]:
        if doc_type == "articles":
            list_text.remove(doc_type)
            doc_type = "article"
        elif doc_type == "bulletins":
            list_text.remove(doc_type)
            doc_type = "bulletin"
        elif doc_type == "rubriques":
            list_text.remove(doc_type)
            doc_type = "rubrique"
        else:
            doc_type = "article"
    else:
        list_text.remove(doc_type)
    cleaned_text = " ".join(list_text)

    return doc_type, cleaned_text


def extract_rubriques(query: str) -> Tuple[List[str], str]:
    """
    Extrait la ou les rubriques demandées dans une requête.
    :param query: La requête à analyser.
    :return: Un tuple (rubrique, requête sans la rubrique)
    """
    # Le texte est sans stop-words à ce stade,
    # il faut donc lister les rubriques sans stop-words.
    list_rubriques = [
        "focus",
        "au coeur regions",
        "evenement",
        "événement",
        "evénement",
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
    text_lower = query.lower()

    # Remplacer tous les " ou " entre les rubriques par juste un espace
    # (on prépare la regex avant de supprimer les rubriques)
    rubrique_pattern = "|".join(re.escape(r) for r in list_rubriques)
    # Cas : rubrique1 ou rubrique2
    text_lower = re.sub(
        rf"({rubrique_pattern})\s+ou\s+({rubrique_pattern})", r"\1 \2", text_lower
    )

    for rubrique in list_rubriques:
        if rubrique in text_lower:
            rubriques.append(rubrique)
            text_lower = text_lower.replace(rubrique, "")

    # Nettoyage des espaces
    cleaned_text = re.sub(r"\s+", " ", text_lower).strip()

    return rubriques, cleaned_text


def extract_keywords(query: str) -> List[str]:
    """
    Extrait les mots-clés d'une requête (à supposer qu'elle ne contienne plus de dates,
    de rubriques, etc.)
    :param query: La requête à analyser.
    :return: Une liste de mots-clés.
    """
    keywords = []
    # 1. Normaliser les apostrophes
    query = query.replace("’", "'")

    # 2. Séparer les mots comme d'ingénieurs → d ingénieurs
    query = re.sub(r"\b(d|l|qu|n|s|c|j|t)'", r"\1 ", query, flags=re.IGNORECASE)

    words = re.findall(r"\b\w+(?:-\w+)*\b", query)
    stopwords_apres_pas = {"de", "du", "des", "d", "la", "le", "les", "l"}

    i = 0
    while i < len(words):
        if words[i].lower() == "pas":
            j = i + 1
            # Sauter les petits mots inutiles entre "pas" et le mot-clé
            while j < len(words) and words[j].lower() in stopwords_apres_pas:
                j += 1
            if j < len(words):
                keywords.append("pas " + words[j])
                i = j + 1
            else:
                i += 1
        else:
            keywords.append(words[i])
            i += 1

    return keywords


def extract_titre(text):
    """
    Description.
    :param text:
    :return:
    """
    titre = None

    # cas titre avec du contenu entre « » ou " " ou ' '
    m = re.search(r'\btitre\s+(["«\'])(.+?)["»\']', text)
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
        text = re.sub(pattern, "", text, count=1)
    else:
        # cas 'titre mot'
        m = re.search(r"\btitre\s+(\S+)", text)
        if m:
            titre_candidate = m.group(1)
            titre = titre_candidate
            text = re.sub(r"\btitre\s+" + re.escape(titre_candidate), "", text, count=1)

    # cas mot avant "titre" (si titre est en dernier)
    if not titre:
        m = re.search(r"\b(\w+)\s+titre\b", text)
        if m:
            titre = m.group(1)
            text = re.sub(r"\b" + re.escape(titre) + r"\s+titre\b", "", text, count=1)

    text_clean = re.sub(r"\s+", " ", text).strip()

    return titre, text_clean


def extract_contenu(text):
    """
    Description.
    :param text:
    :return:
    """
    contenu = None
    # Chercher "contenu <mot>"
    m = re.search(r"\bcontenu\s+(\S+)", text)
    if m:
        contenu = m.group(1)
        # Supprimer "contenu <mot>" du texte
        text = re.sub(r"\bcontenu\s+" + re.escape(contenu), "", text, count=1)
    text_clean = re.sub(r"\s+", " ", text).strip()
    return contenu, text_clean


def extract_date_info(text):
    """
    Description.
    :param text:
    :return:
    """
    original_text = text
    text = text.lower()
    mois_fr = {
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

    def parse_date_string(date_text):
        date_text = date_text.strip()
        m = re.match(r"(\d{1,2})\s+([a-zéèêç]+)\s+(\d{4})", date_text)
        if m:
            jour, mois, annee = m.groups()
            if mois in mois_fr:
                return f"{annee}-{mois_fr[mois]}-{int(jour):02d}"
        m = re.match(r"([a-zéèêç]+)\s+(\d{4})", date_text)
        if m:
            mois, annee = m.groups()
            if mois in mois_fr:
                return f"{annee}-{mois_fr[mois]}-**"
        m = re.match(r"(\d{8})", date_text)
        if m:
            try:
                d = datetime.strptime(m.group(1), "%d%m%Y")
                return d.strftime("%Y-%m-%d")
            except:
                return None
        m = re.match(r"(19|20)\d{2}", date_text)
        if m:
            return f"{m.group(0)}-**-**"
        return None

    def clean_query_only_keywords(text):
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
        text = re.sub(r"\b\d{1,2}\s+(" + mois_pattern + r")\s+\d{4}\b", "", text)
        text = re.sub(r"\b(" + mois_pattern + r")\s+\d{4}\b", "", text)
        text = re.sub(
            r"\b(au mois de|au mois|en|de|du|dans)\s+(" + mois_pattern + r")\b",
            "",
            text,
        )
        text = re.sub(r"\b(19|20)\d{2}\b", "", text)
        text = re.sub(r"\b\d{8}\b", "", text)  # important pour enlever 14062013 etc.
        text = re.sub(
            r"\b(entre|et|avant|après|apres|d’après|d\'apres|depuis|pas au mois de|au mois|mois|à partir)\b",
            "",
            text,
        )
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    result = {}

    # Cas 0 : exclusion avec "pas"
    m = re.search(
        r"pas\s+(au mois de|au mois|en|de|du)?\s*([a-zéèêç]+)(?:[\s,\.]|$)", text
    )
    if m:
        mot = m.group(2)
        if mot in mois_fr:
            result["pas"] = f"****-{mois_fr[mot]}-**"

    # Cas 1 : entre ... et ...
    m = re.search(r"entre\s+(.*?)\s+et\s+(.*)", text)
    if m:
        d1 = parse_date_string(m.group(1))
        d2 = parse_date_string(m.group(2))
        print(d2)
        if d1:
            result["min"] = d1
        if d2:
            result["max"] = d2
        cleaned_query = clean_query_only_keywords(original_text)
        return result, cleaned_query

    # Cas 2 : à partir / après / depuis / d'après
    m = re.search(
        r"(à partir de|à partir|après|apres|d’après|d\'apres|depuis)\s+([^\.,;]*)", text
    )
    if m:
        d = parse_date_string(m.group(2))
        if d:
            result["min"] = d
            cleaned_query = clean_query_only_keywords(original_text)
            return result, cleaned_query

    # Cas 3 : avant
    m = re.search(r"avant\s+(.+?)(?:[\s,\.]|$)", text)
    if m:
        d = parse_date_string(m.group(1))
        if d:
            result["max"] = d
            cleaned_query = clean_query_only_keywords(original_text)
            return result, cleaned_query

    # Cas 4 : en / de / du / dans / au mois
    m = re.search(r"(en|de|du|dans|au mois de|au mois)\s+(.+?)(?:[\s,\.]|$)", text)
    if m:
        d = parse_date_string(m.group(2))
        if d:
            result["exact"] = d
            cleaned_query = clean_query_only_keywords(original_text)
            return result, cleaned_query

    mots = text.split()

    # Cas 5 : sliding window sur 3 mots (jour mois année)
    for i in range(len(mots) - 2):
        triplet = mots[i] + " " + mots[i + 1] + " " + mots[i + 2]
        d = parse_date_string(triplet)
        if d:
            result["exact"] = d
            cleaned_query = clean_query_only_keywords(original_text)
            return result, cleaned_query

    # Cas 6 : sliding window sur 2 mots (mois année)
    for i in range(len(mots) - 1):
        pair = mots[i] + " " + mots[i + 1]
        d = parse_date_string(pair)
        if d:
            result["exact"] = d
            cleaned_query = clean_query_only_keywords(original_text)
            return result, cleaned_query

    # Cas 7 : année seule
    for mot in mots:
        d = parse_date_string(mot)
        if d:
            result["exact"] = d
            cleaned_query = clean_query_only_keywords(original_text)
            return result, cleaned_query

    cleaned_query = clean_query_only_keywords(original_text)
    return result if result else None, cleaned_query


def extract_image(text):
    """
    Description.
    :param text:
    :return:
    """
    if "image" in text:
        if "sans image" in text:
            text = text.replace("sans image", "")
            return 0, text
        text = text.replace("image", "")
        return 1, text
    if "images" in text:
        if "sans images" in text:
            text = text.replace("sans images", "")
            return 0, text
        text = text.replace("images", "")
        return 1, text
    else:
        return None, text


def replace_soit(text):
    """
    Description.
    :param text:
    :return:
    """
    count_soit = 0
    for mot in text.split():
        if mot == "soit":
            count_soit += 1
            print(count_soit)
    if count_soit >= 2:
        text = text.replace("soit", "", 1)
        text = text.replace("soit", "ou")
    return text


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
    return : structure de composants de la requete
    """
    doc_type, texte_liste = extract_doctype(requete_langage_naturel)

    # Enlever les rubriques article ou bulletin à l'intérieur du texte
    texte_liste = texte_liste.split()
    useless_words = [
        "article",
        "articles",
        "bulletin",
        "bulletins",
        "rubrique",
        "rubriques",
    ]
    texte_liste = [word for word in texte_liste if word not in useless_words]
    texte_liste = " ".join(texte_liste)
    print(f"Requête simplifiée : {texte_liste}")

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
    structured_query = {
        "query": requete_langage_naturel,
        "date": date,
        "titre": titre,
        "contenu": contenu,
        "keywords": keywords,
        "rubriques": rubriques,
        "doc_type": doc_type,
        "image": image,
        "texte_liste": texte_liste,
    }

    return structured_query
