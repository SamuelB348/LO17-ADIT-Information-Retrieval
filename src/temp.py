"""
Fichier temporaire
"""

import string
from spellchecker import correcteur_orthographique
import time
import pandas as pd
import matplotlib.pyplot as plt
import re
import calendar
import xml.etree.ElementTree as et
from datetime import datetime


def correction_requetes(requete: str):
    """
    Corrige les requetes en supprimant les 'stop words' (par rapport aux requetes du TD)
    et les ponctuations
    param requete: la requete à corriger
    return: la requete corrigée
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
        "écrits",
        "j’aimerais",
        "dans",
        "quelles",
        "tout",
        "tous",
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
    requete = requete.lower()
    liste_mot_requete = requete.split()
    # print(liste_mot_requete)
    liste_mot_requete2 = liste_mot_requete.copy()
    for mot in liste_mot_requete:
        if mot in liste_stop_words:
            liste_mot_requete2.remove(mot)

    requete_corrigee = " ".join(liste_mot_requete2)
    punct = string.punctuation
    for c in punct:
        requete_corrigee = requete_corrigee.replace(c, "")
    return requete_corrigee


queries = [
    "Afficher la liste des articles qui parlent des systèmes embarqués dans la rubrique Horizons Enseignement.",
    "Je voudrais les articles qui parlent de cuisine moléculaire.",
    "Quels sont les articles sur la réalité virtuelle ?",
    "Je voudrais les articles qui parlent d’airbus ou du projet Taxibot.",
    "Je voudrais les articles qui parlent du tennis.",
    "Je voudrais les articles traitant de la Lune.",
    "Quels sont les articles parus entre le 3 mars 2013 et le 4 mai 2013 évoquant les Etats-Unis ?",
    "Afficher les articles de la rubrique en direct des laboratoires.",
    "Je veux les articles de la rubrique Focus parlant d’innovation.",
    "Quels sont les articles parlant de la Russie ou du Japon ?",
    "Je voudrais les articles de 2011 sur l’enseignement.",
    "Je voudrais les articles dont le titre contient le mot chimie.",
    "Je veux les articles de 2014 et de la rubrique Focus et parlant de la santé.",
    "Je souhaite les rubriques des articles parlant de nutrition ou de vins.",
    "Je cherche les recherches sur l’aéronautique.",
    "Article traitant des Serious Game et de la réalité virtuelle.",
    "Quels sont les articles traitant d’informatique ou de reseaux.",
    "Je voudrais les articles de la rubrique Focus mentionnant un laboratoire.",
    "Quels sont les articles publiés au mois de novembre 2011 portant sur de la recherche.",
    "Je veux des articles sur la plasturgie.",
    "Quels articles portent à la fois sur les nanotechnologies et les microsatellites.",
    "Je voudrais les articles liés à la recherche scientifique publiés en Février 2010.",
    "Donner les articles qui parlent d’apprentissage et de la rubrique Horizons Enseignement.",
    "Chercher les articles dans le domaine industriel et datés à partir de 2012.",
    "Nous souhaitons obtenir les articles du mois de Juin 2013 et parlant du cerveau.",
    "Rechercher tous les articles sur le CNRS et l’innovation à partir de 2013.",
    "Je cherche des articles sur les avions.",
    "Donner les articles qui portent sur l’alimentation de l’année 2013.",
    "Articles dont le titre traite du Tara Oceans Polar Circle.",
    "Je veux des articles parlant de smartphones.",
    "Quels sont les articles parlant de projet européen de l’année 2014 ?",
    "Afficher les articles de la rubrique A lire.",
    "Je veux les articles parlant de Neurobiologie.",
    "Quels sont les articles possédant le mot France ?",
    "Articles écrits en Décembre 2012 qui parlent de l’environnement ?",
    "Quels sont les articles contenant les mots voitures et électrique ?",
    "Je voudrais les articles avec des images dont le titre contient le mot croissance.",
    "Quels sont les articles qui parlent de microbiologie ?",
    "J’aimerais la liste des articles écrits après janvier 2014 et qui parlent d’informatique ou de télécommunications.",
    "Je veux les articles de 2012 qui parlent de l’écologie en France.",
    "Quels articles parlent de réalité virtuelle ?",
    "Dans quelles rubriques trouve-t-on des articles sur l’alimentation ?",
    "Liste des articles qui parlent soit du CNRS, soit des grandes écoles, mais pas de Centrale Paris.",
    "J’aimerais un article qui parle de biologie et qui date d’après le 2 juillet 2012 ?",
    "Quels sont les articles qui parlent d’innovations technologiques ?",
    "Je cherche les articles dont le titre contient le mot performants.",
    "Je voudrais tout les articles provenant de la rubrique événement et contenant le mot congres dans le titre.",
    "Je cherche les articles à propos des fleurs ou des arbres.",
    "Je souhaites avoir tout les articles donc la rubrique est focus ou Actualités Innovations et qui contiennent les mots chercheurs et paris.",
    "Je veux les articles qui parlent du sénégal.",
    "Je voudrais les articles qui parlent d’innovation.",
    "Je voudrais les articles dont le titre contient le mot europe.",
    "Je voudrais les articles qui contiennent les mots Ecole et Polytechnique.",
    "Je cherche les articles provenant de la rubrique en direct des laboratoires.",
    "Je voudrais les articles qui datent du 1 décembre 2012 et dont la rubrique est Actualités Innovations.",
    "Dans quels articles Laurent Lagrost est-il cité ?",
    "Quels articles évoquent la ville de Grenoble ?" "Articles parlant de drones.",
    "Articles parlant de molécules.",
    "Articles contenant une image.",
    "Articles parlant d’université.",
    "Lister tous les articles dont la rubrique est Focus et qui ont des images.",
    "Quels sont les articles dont le titre évoque la recherche ?",
    "Articles dont la rubrique est 'Horizon Enseignement' mais qui ne parlent pas d’ingénieurs.",
    "Tous les articles dont la rubrique est 'En direct des laboratoires' ou 'Focus' et qui évoquent la médecine.",
    "Je voudrais tous les bulletins écrits entre 2012 et 2013 mais pas au mois de juin.",
    "Quels sont les articles dont le titre contient le terme 'marché' et le mot 'projet' ?",
    "Je voudrais les articles dont le titre contient le mot 3D.",
    "Je veux voir les articles de la rubrique Focus et publiés entre 30/08/2011 et 29/09/2011.",
    "Je cherche les articles sur le Changement climatique publiés après 29/09/2011.",
    "Quels articles parlent d’aviation et ont été publiés en 2015 ?",
    "Quels sont les articles de la rubrique évènement qui parlent de la ville de Paris ?",
    "Je veux les articles impliquant le CNRS et qui parlent de chimie.",
    "Trouver les articles qui mentionnent Fink.",
    "Quels articles parlent de la France et de l’Allemagne ?",
    "Je veux les articles parlant de l’Argentine ou du Brésil.",
    "Je veux les articles qui parlent de l’hydravion.",
    "Je veux les articles qui parlent du fauteuil roulant et qui ont pour rubrique Actualité Innovation.",
    "Je veux les articles qui sont écrits en 2012 et parlent du « chrono-environnement ».",
    "Quels sont les articles qui parlent des robots et des chirurgiens ?",
    "Je veux les articles qui parlent des systmes embarqués et non pas la robotique.",
    "Je cherche les articles qui parlent des alimentations ou des agricultures.",
    "Quels sont les articles dont le titre contient le mot histoire ?",
    "Je veux les articles dont le titre est « bi-mot filière agricole ».",
    "Listez-moi les articles qui parlent de 3D et qui sont écrits entre 2010 et 2011.",
    "Quels sont les articles dont le titre contient biocarburant ou le contenu parle des bioénergies ?",
    "Quelle sont les articles qui concernent le CEA ?",
    "Je veux les articles qui parlent philosophie.",
    "Je veux les articles sans image.",
    "Retournez les articles dont le titre contient le mot nucléaire.",
]


# Fonction pour extraire une date au format YYYY-MM-DD
def extract_dates(text):

    # dates dans les formats classiques comme YYYY-MM-DD, DD/MM/YYYY, etc.
    date_patterns = [
        r"\b(\d{4})[-/](\d{2})[-/](\d{2})\b",  # format YYYY-MM-DD ou YYYY/MM/DD
        r"\b(\d{2})[-/](\d{2})[-/](\d{4})\b",  # format DD/MM/YYYY
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_doctype(text):
    text = text.lower()
    texte_liste = text.split()
    doc_type = texte_liste[0]
    if doc_type not in ["article", "bulletin", "rubrique"]:
        if doc_type == "articles":
            texte_liste.remove(doc_type)
            doc_type = "article"
        elif doc_type == "bulletins":
            texte_liste.remove(doc_type)
            doc_type = "bulletin"
        elif doc_type == "rubriques":
            texte_liste.remove(doc_type)
            doc_type = "rubrique"
        else:
            doc_type = "article"
    else:
        texte_liste.remove(doc_type)
    texte_liste = " ".join(texte_liste)
    return doc_type, texte_liste


def replace_soit(text):
    count_soit = 0
    for mot in text.split():
        if mot == "soit":
            count_soit += 1
            print(count_soit)
    if count_soit >= 2:
        text = text.replace("soit", "", 1)
        text = text.replace("soit", "ou")
    return text


def extract_rubriques(text):
    rubriques = [
        "focus",
        "au coeur regions",
        "evenement",
        "actualité innovation",
        "en direct laboratoires",
        "a lire",
        "horizon enseignement",
        "horizons enseignement",
        "actualités innovations",
        "du côté pôles",
        "horizons formation enseignement",
        "horizon formation",
        "en direct labos",
        "du côté pôles",
        "actualités innovation",
        "direct laboratoires",
    ]

    found_rubriques = []
    text_lower = text.lower()

    # Remplacer tous les " ou " entre les rubriques par juste un espace
    # (on prépare la regex avant de supprimer les rubriques)
    rubrique_pattern = "|".join(re.escape(r) for r in rubriques)
    # Cas : rubrique1 ou rubrique2
    text_lower = re.sub(
        rf"({rubrique_pattern})\s+ou\s+({rubrique_pattern})", r"\1 \2", text_lower
    )

    # Ensuite extraction classique
    for rubrique in rubriques:
        if rubrique in text_lower:
            found_rubriques.append(rubrique)
            text_lower = text_lower.replace(rubrique, "")

    # Nettoyage des espaces
    text_clean = re.sub(r"\s+", " ", text_lower).strip()

    return found_rubriques, text_clean


# extraire des mots-clés et des rubriques
def extract(text):
    keywords = []
    # 1. Normaliser les apostrophes
    text = text.replace("’", "'")

    # 2. Séparer les mots comme d'ingénieurs → d ingénieurs
    text = re.sub(r"\b(d|l|qu|n|s|c|j|t)'", r"\1 ", text, flags=re.IGNORECASE)

    words = re.findall(r"\b\w+\b", text)
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
    import re
    from datetime import datetime

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
    if "image" in text:
        if "sans image" in text:
            text = text.replace("sans image", "")
            return 0, text
        else:
            text = text.replace("image", "")
            return 1, text
    elif "images" in text:
        if "sans images" in text:
            text = text.replace("sans images", "")
            return 0, text
        else:
            text = text.replace("images", "")
            return 1, text
    else:
        return None, text


def traitement_requete(requete_langage_naturel):
    """
    Traite une requête en langage naturel pour extraire des informations structurées.

    param requete_langage_naturel: La requête en langage naturel saisie par l'utilisateur, contenant des informations sur les critères de recherche dans l'archive ADIT.
    return: Un dictionnaire contenant les éléments extraits de la requête, incluant :
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
    keywords = extract(texte_liste)

    # structure de la requête
    structured_query = {
        "query": requete_langage_naturel,
        "date": date,
        "titre": titre,
        "contenu": contenu,
        "keywords": keywords,
        "rubriques": rubriques,
        "doc_type": doc_type,
        "date": date,
        "image": image,
        "texte_liste": texte_liste,
    }

    return structured_query


def get_last_day_of_month(year, month):
    # Pour le mois et l'année donnés, on renvoie le dernier jour du mois
    # calendar.monthrange renvoie une tuple (numéro du jour de la semaine pour le 1er jour du mois, nombre de jours dans le mois)
    _, last_day = calendar.monthrange(year, month)
    return last_day


def get_min_max_dates(date_str):
    # Nettoyage de la chaîne de caractères pour enlever les étoiles
    cleaned_date = date_str.replace("*", "")
    while cleaned_date.endswith("-"):
        cleaned_date = cleaned_date[:-1]

    # Fonction pour obtenir le dernier jour du mois
    def get_last_day_of_month(year, month):
        # Pour le mois et l'année donnés, on renvoie le dernier jour du mois
        # calendar.monthrange renvoie une tuple (numéro du jour de la semaine pour le 1er jour du mois, nombre de jours dans le mois)
        _, last_day = calendar.monthrange(year, month)
        return last_day

    print(cleaned_date)
    # Si la date est juste une année (comme "2012-**-**")
    if len(cleaned_date) == 4:  # Format "YYYY-**-**"
        min_date = f"{cleaned_date}-01-01"
        max_date = f"{cleaned_date}-12-31"
    elif len(cleaned_date) == 7:  # Format "YYYY-MM-**"
        year, month = cleaned_date.split("-")
        year = int(year)
        month = int(month)
        min_date = f"{year}-{month:02d}-01"
        max_day = get_last_day_of_month(year, month)
        max_date = f"{year}-{month:02d}-{max_day:02d}"
    elif len(cleaned_date) == 10:  # Format "YYYY-MM-DD"
        year, month, day = cleaned_date.split("-")
        min_date = f"{year}-{month}-{day}"
        max_date = f"{year}-{month}-{day}"

    return min_date, max_date


def replace_min_and_max(date_dict):
    if "min" in date_dict:
        date_dict["min"] = date_dict["min"].replace("*", "")
        while date_dict["min"].endswith("-"):
            date_dict["min"] = date_dict["min"][:-1]
        if len(date_dict["min"]) == 4:  # Format "YYYY-**-**"
            date_dict["min"] = f"{date_dict['min']}-01-01"

        elif len(date_dict["min"]) == 7:  # Format "YYYY-MM-**"
            year, month = date_dict["min"].split("-")
            year = int(year)
            month = int(month)
            date_dict["min"] = f"{year}-{month:02d}-01"
        elif len(date_dict["min"]) == 10:  # Format "YYYY-MM-DD"
            year, month, day = date_dict["min"].split("-")
            date_dict["min"] = f"{year}-{month}-{day}"
        # Retourner les dates sous le format jj/mm/yyyy
        date_dict["min"] = datetime.strptime(date_dict["min"], "%Y-%m-%d")
        date_dict["min"] = date_dict["min"].strftime("%d/%m/%Y")

    if "max" in date_dict:
        date_dict["max"] = date_dict["max"].replace("*", "")
        while date_dict["max"].endswith("-"):
            date_dict["max"] = date_dict["max"][:-1]
        if len(date_dict["max"]) == 4:  # Format "YYYY-**-**"
            date_dict["max"] = f"{date_dict['max']}-12-31"
        elif len(date_dict["max"]) == 7:  # Format "YYYY-MM-**"
            year, month = date_dict["max"].split("-")
            year = int(year)
            month = int(month)
            max_day = get_last_day_of_month(year, month)
            date_dict["max"] = f"{year}-{month:02d}-{max_day:02d}"
        elif len(date_dict["max"]) == 10:  # Format "YYYY-MM-DD"
            year, month, day = date_dict["max"].split("-")
            date_dict["max"] = f"{year}-{month}-{day}"
        # Retourner les dates sous le format jj/mm/yyyy
        date_dict["max"] = datetime.strptime(date_dict["max"], "%Y-%m-%d")
        date_dict["max"] = date_dict["max"].strftime("%d/%m/%Y")


def moteur(requete_langage_naturel):
    # Etape 1
    requete_corrige = correction_requetes(replace_soit(requete_langage_naturel))
    composants = traitement_requete(requete_corrige)
    print(composants)
    # Etape 2
    if composants["titre"] is not None:
        composants["titre"] = correcteur_orthographique(
            composants["titre"], "../lemma_stemmer.txt", 1, 12, 54
        )
    if composants["contenu"] is not None:
        composants["contenu"] = correcteur_orthographique(
            composants["contenu"], "../lemma_stemmer.txt", 1, 12, 54
        )
    if composants["keywords"] is not None:
        print(composants["keywords"])
        for word in composants["keywords"]:
            if word == "ou":
                continue
            elif not word.startswith("pas "):
                composants["keywords"][composants["keywords"].index(word)] = (
                    correcteur_orthographique(
                        word, "../lemma_stemmer.txt", 1, 12, 54
                    ).strip()
                )
            else:
                composants["keywords"][composants["keywords"].index(word)] = (
                    "pas "
                    + correcteur_orthographique(
                        word[4:], "../lemma_stemmer.txt", 1, 12, 54
                    ).strip()
                )
        # Etape 3

    with open("data/index_inverse.txt", "r", encoding='utf-8') as f:
        lignes = f.readlines()

    # Nettoyage des lignes
    donnees = []
    for ligne in lignes:
        parties = ligne.strip().split(",")
        # propres = [parties[0].strip()] + [x.strip().split(':')[0] for x in parties[1:]]
        donnees.append(parties)

    # Création du DataFrame
    df = pd.DataFrame(donnees)

    docs_date = []
    dates_liste = []
    if composants["date"] is not None:
        if "exact" in composants["date"]:
            date = composants["date"]["exact"]
            composants["date"]["min"], composants["date"]["max"] = get_min_max_dates(
                date
            )
            del composants["date"]["exact"]
        replace_min_and_max(composants["date"])
        print(composants["date"])
        if "min" in composants["date"] and "max" in composants["date"]:
            for value in df[0]:
                try:
                    date_value = datetime.strptime(value, "%d/%m/%Y")
                    date_min = datetime.strptime(composants["date"]["min"], "%d/%m/%Y")
                    date_max = datetime.strptime(composants["date"]["max"], "%d/%m/%Y")
                    if date_min <= date_value <= date_max:
                        dates_liste.append(value)
                except ValueError:
                    pass

        elif "min" in composants["date"]:
            for value in df[0]:
                try:
                    date_value = datetime.strptime(value, "%d/%m/%Y")
                    date_min = datetime.strptime(composants["date"]["min"], "%d/%m/%Y")
                    if date_min <= date_value:
                        dates_liste.append(value)
                except ValueError:
                    pass
        elif "max" in composants["date"]:
            for value in df[0]:
                try:
                    date_value = datetime.strptime(value, "%d/%m/%Y")
                    date_max = datetime.strptime(composants["date"]["max"], "%d/%m/%Y")
                    if date_value <= date_max:
                        dates_liste.append(value)
                except ValueError:
                    pass
        if "pas" in composants["date"]:
            # dates_liste = [datetime.strptime(d, "%d/%m/%Y") for d in dates_liste]
            pas_pattern = composants["date"]["pas"]
            pas_pattern = pas_pattern.replace("****", ".*")
            pas_pattern = pas_pattern.replace("**", ".*")
            annee = pas_pattern[0:2]
            mois = pas_pattern[3:5]
            jour = pas_pattern[6:8]
            pas_pattern = f"{jour}/{mois}/{annee}"
            dates_filtre = [d for d in dates_liste if not re.fullmatch(pas_pattern, d)]
        else:
            dates_filtre = dates_liste

        for date in dates_filtre:
            docs_date += df[df[0] == date].iloc[:, 1:].values.flatten().tolist()
    docs_date = [doc for doc in docs_date if doc is not None and pd.notna(doc)]

    for doc in docs_date:
        element_type = doc.split(":")[1]
        if element_type != "date":
            docs_date.remove(doc)
    docs_date = set(docs_date)

    # Etape 4
    docs_rubrique = []
    if composants["rubriques"] is not None:
        for rubrique in composants["rubriques"]:
            docs_rubrique += df[df[0] == rubrique].iloc[:, 1:].values.flatten().tolist()
        docs_rubrique = [
            doc for doc in docs_rubrique if doc is not None and pd.notna(doc)
        ]
        # ou
        docs_rubrique = list(set(docs_rubrique))
    for doc in docs_rubrique:
        element_type = doc.split(":")[1]
        if element_type != "rubrique":
            docs_rubrique.remove(doc)

    docs_titre = set()
    if composants["titre"] is not None:
        titre_nettoye = composants["titre"].strip()  # retire les espaces en trop
        docs_titre = df[df[0] == titre_nettoye].iloc[:, 1:].values.flatten().tolist()
        docs_titre = [doc for doc in docs_titre if doc and pd.notna(doc)]

        # Filtrage des docs de type 'titre'
        docs_titre_copy = docs_titre.copy()
        for doc in docs_titre_copy:
            if ":" not in doc:
                docs_titre.remove(doc)
                continue
            type_element = doc.split(":")[1].strip()
            if type_element != "titre":
                docs_titre.remove(doc)

        # Extraction des doc_id sans espace
        docs_titre = set(doc.split(":")[0].strip() for doc in docs_titre if ":" in doc)

    docs_contenu = set()
    if composants["contenu"] is not None:
        contenu_nettoye = composants["contenu"].strip()
        docs_contenu = (
            df[df[0] == contenu_nettoye].iloc[:, 1:].values.flatten().tolist()
        )
        docs_contenu = [doc for doc in docs_contenu if doc and pd.notna(doc)]

        # Filtrage par type 'texte'
        docs_contenu_copy = docs_contenu.copy()
        for doc in docs_contenu_copy:
            if doc is None or ":" not in doc:
                docs_contenu.remove(doc)
                continue
            element_type = doc.split(":")[1].strip()
            if element_type != "texte":
                docs_contenu.remove(doc)

        # Extraction des doc_id propres
        docs_contenu = set(
            [doc.split(":")[0].strip() for doc in docs_contenu if doc and ":" in doc]
        )
    else:
        docs_contenu = set()

    docs_non_keywords = df.iloc[:, 1:].values.flatten().tolist()
    docs_non_keywords = [
        doc for doc in docs_non_keywords if doc is not None and pd.notna(doc)
    ]
    docs_non_keywords = set(docs_non_keywords)

    pas_keywords_remove = None
    if composants["keywords"] is not None:
        for i, keyword in enumerate(composants["keywords"]):
            if keyword.startswith("pas "):
                pas_keywords_remove = keyword
                pas_keywords = keyword.split()
                pas_keywords = pas_keywords[1:]

                for pas_keyword in pas_keywords:
                    docs_non_keywords &= set(
                        df[df[0] == pas_keyword].iloc[:, 1:].values.flatten().tolist()
                    )

                docs_non_keywords_copy = docs_non_keywords.copy()

                for doc in docs_non_keywords_copy:
                    element_type = doc.split(":")[1]
                    if (element_type != "texte") and (element_type != "titre"):
                        docs_non_keywords.remove(doc)

    if pas_keywords_remove is not None:
        composants["keywords"].remove(pas_keywords_remove)
    else:
        docs_non_keywords = set()

    # le ou
    docs_keywords = df.iloc[:, 1:].values.flatten().tolist()
    docs_keywords = [doc for doc in docs_keywords if doc is not None and pd.notna(doc)]
    docs_keywords = set(docs_keywords)

    if len(composants["keywords"]) == 1 and composants["keywords"][0] == "ou":
        doc_retourne = set(docs_titre) | set(docs_contenu)
        return doc_retourne, composants["doc_type"]

    elif "ou" in composants["keywords"]:
        liste_ou = composants["keywords"].index("ou")
        liste_ou1 = composants["keywords"][:liste_ou]
        liste_ou2 = composants["keywords"][liste_ou + 1 :]
        docs_liste1 = df.iloc[:, 1:].values.flatten().tolist()
        docs_liste1 = [doc for doc in docs_liste1 if doc is not None and pd.notna(doc)]
        docs_liste1 = set(docs_liste1)
        docs_liste2 = df.iloc[:, 1:].values.flatten().tolist()
        docs_liste2 = [doc for doc in docs_liste2 if doc is not None and pd.notna(doc)]
        docs_liste2 = set(docs_liste2)

        for keyword in liste_ou1:
            docs_liste1 &= set(
                df[df[0] == keyword].iloc[:, 1:].values.flatten().tolist()
            )

        for keyword in liste_ou2:
            docs_liste2 &= set(
                df[df[0] == keyword].iloc[:, 1:].values.flatten().tolist()
            )
        docs_keywords = docs_liste1 | docs_liste2
    else:
        print(composants["keywords"])
        for keyword in composants["keywords"]:
            docs_keywords &= set(
                df[df[0] == keyword].iloc[:, 1:].values.flatten().tolist()
            )

    # print(docs_keywords)
    # print(docs_date)
    # print(docs_rubrique)
    # IMAGES
    docs_image = []
    if composants["image"] is not None:
        docs_image += (
            df[df[0] == "presence_image"].iloc[:, 1:].values.flatten().tolist()
        )
        docs_image = [doc for doc in docs_image if doc is not None and pd.notna(doc)]

    docs_date = set([doc.split(":")[0] for doc in docs_date])
    docs_rubrique = set([doc.split(":")[0] for doc in docs_rubrique])
    docs_titre = set([doc.split(":")[0] for doc in docs_titre])
    docs_contenu = set([doc.split(":")[0] for doc in docs_contenu])
    docs_keywords = set([doc.split(":")[0] for doc in docs_keywords])
    docs_image = set([doc.split(":")[0] for doc in docs_image])

    docs_possibles = [
        docs_date,
        docs_rubrique,
        docs_image,
        docs_titre,
        docs_contenu,
        docs_keywords,
        docs_image,
    ]
    docs_possibles = [set(docs) for docs in docs_possibles if len(docs) != 0]

    print(f"Docs sur keywords : {docs_keywords}")
    print(f"Docs non keywords : {docs_non_keywords}")
    print(f"Docs sur titre : {docs_titre}")
    print(f"Docs sur contenu : {docs_contenu}")
    print(f"Docs sur date : {docs_date}")
    print(f"Docs sur rubrique : {docs_rubrique}")
    print(f"Docs sur image : {docs_image}")

    if docs_possibles == []:
        return None, composants["doc_type"]
    intersect = set.intersection(*docs_possibles)

    docs_non_keywords_ids = set()
    for doc in docs_non_keywords:
        if doc and ":" in doc:
            doc_id = doc.split(":")[0].strip()
            docs_non_keywords_ids.add(doc_id)

    # Nettoyer et filtrer l'intersection
    intersect = {doc.strip() for doc in intersect}
    intersect -= docs_non_keywords_ids

    final_intersect = intersect

    if composants["doc_type"] == "article":
        return final_intersect, composants["doc_type"]

    elif composants["doc_type"] == "rubrique":
        resultat = []
        for article in final_intersect:
            mask = df.apply(
                lambda ligne: f"{article}:rubrique"
                in map(lambda v: str(v).strip(), ligne.values),
                axis=1,
            )
            match = df.loc[mask, 0]
            if not match.empty:
                resultat.append(match.iloc[0].strip())

        return set(resultat), composants["doc_type"]

    elif composants["doc_type"] == "bulletin":
        resultat = []
        for article in final_intersect:
            mask = df.apply(
                lambda ligne: f"{article}:numero" in map(str, ligne.values), axis=1
            )
            match = df.loc[mask, 0]
            if not match.empty:
                resultat.append(match.iloc[0])
        return set(resultat), composants["doc_type"]
    return set(), 'article'

# # Exemple d'utilisation
# requete = "rubrique 2014 et rubrique focus et santé"
# requetes_test = [
#     "Je voudrais les articles qui parlent de cuisine moléculaire.",  # ok
#     "Quels sont les articles sur la réalité virtuelle?",  # ok
#     "Je voudrais les articles qui parlent d’airbus ou du projet Taxibot.",  # ok
#     "Je voudrais tous les bulletins écrits entre 2012 et 2013 mais pas au mois de juin.",  # ok
#     "Quels sont les articles dont le titre contient biocarburant ou le contenu parle des bioénergies ?",  # ok
#     "Je souhaite les rubriques des articles parlant de nutrition ou de vins.",  # ok
#     "Articles dont la rubrique est 'Horizon Enseignement' mais qui ne parlent pas d’ingénieurs.",  # ok
#     "Quels sont les articles dont le titre contient le mot chimie?",  # ok
#     "Lister tous les articles dont la rubrique est Focus et qui ont des images.",  # ok
#     "Je veux les articles de 2014 et de la rubrique Focus et parlant de la santé.",  # ok
# ]
#
#
# for query in requetes_test:
#     print("#####################################################")
#     print(f"Requête : {query}")
#     print(f"Liste de documents trouvés : {moteur(query)}")



# def extraire_fichiers_filtrés(xml_path):
#     """
#     Renvoie les valeurs <fichier> des articles datés entre 2013 et 2014,
#     mais pas au mois de juin.
#
#     :param xml_path: chemin du fichier corpus.xml
#     :return: liste des identifiants <fichier> correspondants
#     """
#     tree = et.parse(xml_path)
#     root = tree.getroot()
#
#     fichiers = []
#
#     for article in root.findall("article"):
#         date_str = article.findtext("date")
#         try:
#             date_obj = datetime.strptime(date_str, "%d/%m/%Y")
#         except (TypeError, ValueError):
#             continue
#
#         if 2012 <= date_obj.year <= 2013 and date_obj.month != 6:
#             fichier = article.findtext("numero")
#             if fichier:
#                 fichiers.append(fichier)
#
#     return fichiers


# def fichiers_rubrique_focus_avec_images(xml_path):
#     """
#     Renvoie la liste des fichiers dont la rubrique est 'Focus' et qui contiennent des images.
#
#     :param xml_path: chemin vers le fichier corpus.xml
#     :return: liste des identifiants <fichier> correspondants
#     """
#     tree = et.parse(xml_path)
#     root = tree.getroot()
#
#     fichiers = []
#
#     for article in root.findall("article"):
#         rubrique = article.findtext("rubrique")
#         images_element = article.find("images")
#
#         # Vérifie que la rubrique est "Focus" et que <images> contient au moins une <image>
#         if rubrique.lower() == "focus" and images_element is not None:
#             if images_element.find("image") is not None:
#                 fichier = article.findtext("fichier")
#                 if fichier:
#                     fichiers.append(fichier)
#
#     return fichiers


# resultats = fichiers_rubrique_focus_avec_images("corpus_clean (5) (2).xml")
# print(resultats)
#
# def moteur_simule(requete):
#     return requete_to_docs.get(requete, [])
#
# # -Jeu de test : 10 requetes du TD6
# requetes_test = [
#     "Je voudrais les articles qui parlent de cuisine moléculaire.",  # ok
#     "Quels sont les articles sur la réalité virtuelle?",  # ok
#     "Je voudrais les articles qui parlent d’airbus ou du projet Taxibot.",  # ok
#     "Je voudrais tous les bulletins écrits entre 2012 et 2013 mais pas au mois de juin.",  # ok
#     "Quels sont les articles dont le titre contient biocarburant ou le contenu parle des bioénergies ?",  # ok
#     "Je souhaite les rubriques des articles parlant de nutrition ou de vins.",  # ok
#     "Articles dont la rubrique est 'Horizon Enseignement' mais qui ne parlent pas d’ingénieurs.",  # ok
#     "Quels sont les articles dont le titre contient le mot chimie?",  # ok
#     "Lister tous les articles dont la rubrique est Focus et qui ont des images.",  # ok
#     "Je veux les articles de 2014 et de la rubrique Focus et parlant de la santé.",  # ok
# ]
#
#
# # Docs pertinents définis manuellement pour chaque requête
# docs_pertinents = {
#     requetes_test[0]: {"74752"},
#     requetes_test[1]: {"70421", "70162", "74168", "75064"},
#     requetes_test[2]: {"72933", "67797", "74745", "72636", "71617", "68383", "70920"},
#     requetes_test[3]: {
#         "272",
#         "284",
#         "267",
#         "273",
#         "282",
#         "277",
#         "286",
#         "275",
#         "278",
#         "266",
#         "285",
#         "270",
#         "274",
#         "276",
#         "287",
#         "283",
#         "269",
#         "268",
#         "279",
#         "280",
#     },
#     requetes_test[4]: {"68385", "72121"},
#     requetes_test[5]: {
#         "focus",
#         "au coeur des régions",
#         "evénement",
#         "actualité innovation",
#         "du côté des pôles",
#         "actualités innovations",
#     },
#     requetes_test[6]: {"73437", "72636", "72637"},
#     requetes_test[7]: {"67561", "68278", "75461"},
#     requetes_test[8]: {
#         "67794",
#         "67795",
#         "67937",
#         "67938",
#         "68274",
#         "68276",
#         "68383",
#         "68638",
#         "68881",
#         "68882",
#         "69177",
#         "69178",
#         "69179",
#         "69811",
#         "70161",
#         "70420",
#         "70421",
#         "70422",
#         "70914",
#         "70916",
#         "71612",
#         "71614",
#         "71835",
#         "71836",
#         "71837",
#         "72113",
#         "72114",
#         "72115",
#         "72392",
#         "72629",
#         "72932",
#         "72933",
#         "73182",
#         "73183",
#         "73185",
#         "73430",
#         "73431",
#         "73683",
#         "73684",
#         "73875",
#         "73876",
#         "74167",
#         "74168",
#         "74450",
#         "75063",
#         "75064",
#         "75065",
#         "75457",
#         "75458",
#         "75788",
#         "75789",
#         "75790",
#         "76206",
#         "76207",
#         "76507",
#         "76508",
#     },
#     requetes_test[9]: {"76507", "75459", "75458"},
# }
#
# # Réponses simulées du moteur
# requete_to_docs = {
#     "Je voudrais les articles qui parlent de cuisine moléculaire.": ["74752"],  # ok
#     "Quels sont les articles sur la réalité virtuelle?": [
#         "70421",
#         "75064",
#         "74168",
#         "70162",
#     ],  # manque le 70162
#     "Je voudrais les articles qui parlent d’airbus ou du projet Taxibot.": [
#         "67797",
#         "74745",
#         "72933",
#         "71617",
#         "70920",
#         "72636",
#         "68383",
#     ],
#     "Je voudrais tous les bulletins écrits entre 2012 et 2013 mais pas au mois de juin.": [
#         "272",
#         "284",
#         "267",
#         "273",
#         "282",
#         "277",
#         "286",
#         "275",
#         "278",
#         "266",
#         "285",
#         "270",
#         "274",
#         "276",
#         "287",
#         "283",
#         "269",
#         "268",
#         "279",
#         "280",
#     ],
#     "Quels sont les articles dont le titre contient biocarburant ou le contenu parle des bioénergies ?": [
#         "72121",
#         "68385",
#     ],
#     "Je souhaite les rubriques des articles parlant de nutrition ou de vins.": [
#         "focus",
#         "evénement",
#         "au coeur des régions",
#         "actualité innovation",
#         "du côté des pôles",
#         "actualités innovations",
#     ],
#     "Articles dont la rubrique est 'Horizon Enseignement' mais qui ne parlent pas d’ingénieurs.": [
#         "72636",
#         "72637",
#         "73437",
#     ],
#     "Quels sont les articles dont le titre contient le mot chimie?": [
#         "75461",
#         "68278",
#         "67561",
#     ],
#     "Lister tous les articles dont la rubrique est Focus et qui ont des images.": [
#         "72933",
#         "73684",
#         "75065",
#         "70421",
#         "75458",
#         "67937",
#         "73430",
#         "71614",
#         "73683",
#         "72114",
#         "67794",
#         "72113",
#         "75788",
#         "75063",
#         "73183",
#         "76508",
#         "75457",
#         "73182",
#         "75789",
#         "69177",
#         "70420",
#         "68274",
#         "76207",
#         "75790",
#         "75064",
#         "73185",
#         "68881",
#         "73876",
#         "71835",
#         "74168",
#         "71836",
#         "72932",
#         "71837",
#         "67795",
#         "72392",
#         "70161",
#         "71612",
#         "68638",
#         "67938",
#         "69178",
#         "70916",
#         "76507",
#         "76206",
#         "72115",
#         "73431",
#         "70422",
#         "74167",
#         "68882",
#         "68383",
#         "72629",
#         "74450",
#         "73875",
#         "69179",
#         "69811",
#         "68276",
#         "70914",
#     ],
#     "Je veux les articles de 2014 et de la rubrique Focus et parlant de la santé.": [
#         "76507",
#         "75458",
#         "75459",
#     ],
# }
#
#
# resultats = []
#
# for requete in requetes_test:
#     pertinents = docs_pertinents[requete]
#     systeme = set(moteur_simule(requete))
#
#     tp = len(pertinents & systeme)
#     fp = len(systeme - pertinents)
#     fn = len(pertinents - systeme)
#
#     precision = tp / (tp + fp) if tp + fp > 0 else 0
#     rappel = tp / (tp + fn) if tp + fn > 0 else 0
#     f_mesure = (
#         2 * (precision * rappel) / (precision + rappel)
#         if (precision + rappel) > 0
#         else 0
#     )
#
#     # Mesure du temps de réponse moyen
#     start = time.time()
#     for _ in range(100):
#         moteur_simule(requete)
#     end = time.time()
#     temps_moyen_ms = round((end - start) / 100 * 1000, 3)
#
#     resultats.append(
#         {
#             "requête": requete,
#             "precision": round(precision, 2),
#             "rappel": round(rappel, 2),
#             "f_mesure": round(f_mesure, 2),
#             "temps (ms)": temps_moyen_ms,
#         }
#     )
#
# df = pd.DataFrame(resultats)
# print(df)
#
# df_plot = df[["requête", "precision", "rappel", "f_mesure"]].set_index("requête")
# df_plot.plot(kind="bar", figsize=(12, 6), title="Évaluation du moteur (10 requêtes)")
# plt.ylabel("Score")
# plt.xticks(rotation=45, ha="right")
# plt.tight_layout()
# plt.grid(axis="y")
# plt.show()

# Liste de requêtes à tester
# requetes_test = [
#     "Je voudrais les articles qui parlent de cuisine moléculaire.",
#     "Quels sont les articles sur la réalité virtuelle?",
#     "Je voudrais les articles qui parlent d’airbus ou du projet Taxibot.",
#     # "Je voudrais tous les bulletins écrits entre 2012 et 2013 mais pas au mois de juin.", la partie bulletin est lente
#     "Quels sont les articles dont le titre contient biocarburant ou le contenu parle des bioénergies ?",
#     "Je souhaite les rubriques des articles parlant de nutrition ou de vins.",
#     "Articles dont la rubrique est 'Horizon Enseignement' mais qui ne parlent pas d’ingénieurs.",
#     "Quels sont les articles dont le titre contient le mot chimie?",
#     "Lister tous les articles dont la rubrique est Focus et qui ont des images.",
#     "Je veux les articles de 2014 et de la rubrique Focus et parlant de la santé.",
# ]
#
# temps_moyens = {}
#
# # boucle sur chaque requête (les 9)
# for requete in requetes_test:
#     temps_total = 0
#     for _ in range(100):
#         debut = time.time()
#         moteur(requete)
#         fin = time.time()
#         temps_total += fin - debut
#     temps_moyens[requete] = round(temps_total / 100, 4)
#
# #  graphique
# plt.figure(figsize=(14, 6))
# plt.bar(
#     range(len(temps_moyens)),
#     list(temps_moyens.values()),
#     tick_label=[f"Q{i+1}" for i in range(len(temps_moyens))],
# )
# plt.xlabel("Requête (abrégée)")
# plt.ylabel("Temps moyen (secondes)")
# plt.title("Temps de réponse moyen du moteur (100 exécutions)")
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()
#
# for i, (req, t) in enumerate(temps_moyens.items()):
#     print(f"Q{i+1} : {t:.4f} sec — {req}")
#
# requete_lente = (
#     "Je voudrais tous les bulletins écrits entre 2012 et 2013 mais pas au mois de juin."
# )
#
# temps_execution = []
# for _ in range(4):
#     debut = time.time()
#     moteur(requete_lente)
#     fin = time.time()
#     temps_execution.append(fin - debut)
#
# temps_moyen = round(sum(temps_execution) / len(temps_execution), 4)
# print(f"Temps moyen pour la requête bulletins : {temps_moyen} secondes")
#
# plt.figure(figsize=(10, 5))
# plt.plot(temps_execution, marker="o")
# plt.xlabel("Exécution")
# plt.ylabel("Temps (secondes)")
# plt.title("Temps d'exécution pour 4 recherches de bulletins")
# plt.grid(True)
# plt.tight_layout()
# plt.show()
