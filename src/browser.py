"""
Fonction principale qui permet la recherche d'information à partir d'une requête.
"""

import re
import calendar
from datetime import datetime
import pandas as pd
from queries import clean_query, traitement_requete, replace_soit
from spellchecker import correcteur_orthographique


def get_last_day_of_month(year, month):
    """
    Desc.
    :param year:
    :param month:
    :return:
    """
    # Pour le mois et l'année donnés, on renvoie le dernier jour du mois
    # calendar.monthrange renvoie un tuple (numéro du jour de la semaine pour le 1er jour du mois,
    # nombre de jours dans le mois)
    _, last_day = calendar.monthrange(year, month)
    return last_day


def get_min_max_dates(date_str):
    """
    Description.
    :param date_str:
    :return:
    """
    # Nettoyage de la chaîne de caractères pour enlever les étoiles
    cleaned_date = date_str.replace("*", "")
    while cleaned_date.endswith("-"):
        cleaned_date = cleaned_date[:-1]

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
    else:
        raise ValueError(f"{date_str} format invalide")

    return min_date, max_date


def replace_min_and_max(date_dict):
    """
    Description.
    :param date_dict:
    :return:
    """
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
    """
    Description.
    :param requete_langage_naturel:
    :return:
    """

    liste_required = []
    composants = traitement_requete(clean_query(replace_soit(requete_langage_naturel)))
    print(composants)

    if composants["titre"] is not None:
        composants["titre"] = correcteur_orthographique(
            composants["titre"], "data/lemma_stemmer.txt", 1, 12, 54
        )
    if composants["contenu"] is not None:
        composants["contenu"] = correcteur_orthographique(
            composants["contenu"], "data/lemma_stemmer.txt", 1, 12, 54
        )
    if composants["keywords"] is not None:
        print(composants["keywords"])
        for word in composants["keywords"]:
            if word == "ou":
                continue
            if not word.startswith("pas "):
                composants["keywords"][composants["keywords"].index(word)] = (
                    correcteur_orthographique(
                        word, "data/lemma_stemmer.txt", 1, 12, 54
                    ).strip()
                )
            else:
                composants["keywords"][composants["keywords"].index(word)] = (
                    "pas "
                    + correcteur_orthographique(
                        word[4:], "data/lemma_stemmer.txt", 1, 12, 54
                    ).strip()
                )
        # Etape 3

    with open("data/index_inverse.txt", "r", encoding="utf-8") as f:
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
        liste_required.append("date")
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
    dico_rubriques = {
        "focus": "focus",
        "au coeur regions" : "au coeur des régions",
        "evenement" : "evénement",
        "evénement" : "evénement",
        "événement" : "événement",
        "actualité innovation" : "actualité innovation",
        "actualités innovation" : "actualités innovation",
        "actualités innovations": "actualités innovations",
        "direct laboratoires" : "en direct des laboratoires",
        "direct labos": "en direct des labos",
        "a lire" : "a lire",
        "horizon enseignement" : "horizon enseignement",
        "horizons enseignement" : "horizons enseignement",
        "horizons formation enseignement": "horizon formation enseignement",
        "horizon formation": "horizon formation",
        "côté pôles" : "du côté des pôles",
    }
    docs_rubrique = []
    if composants["rubriques"] is not None and composants["rubriques"]:
        liste_required.append("rubrique")
        for rubrique in composants["rubriques"]:
            docs_rubrique += df[df[0] == dico_rubriques[rubrique]].iloc[:, 1:].values.flatten().tolist()
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
        liste_required.append("titre")
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
        liste_required.append("contenu")
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
            doc.split(":")[0].strip() for doc in docs_contenu if doc and ":" in doc
        )
    else:
        docs_contenu = set()

    docs_non_keywords = df.iloc[:, 1:].values.flatten().tolist()
    docs_non_keywords = [
        doc for doc in docs_non_keywords if doc is not None and pd.notna(doc)
    ]
    docs_non_keywords = set(docs_non_keywords)

    pas_keywords_remove = None
    if composants["keywords"] is not None and composants["keywords"]:
        liste_required.append("keywords")
        for _, keyword in enumerate(composants["keywords"]):
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
                    if element_type not in ("texte", "titre"):
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

    if "ou" in composants["keywords"]:
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
        liste_required.append("images")
        docs_image += (
            df[df[0] == "presence_image"].iloc[:, 1:].values.flatten().tolist()
        )
        docs_image = [doc for doc in docs_image if doc is not None and pd.notna(doc)]

    docs_date = set(doc.split(":")[0] for doc in docs_date)
    docs_rubrique = set(doc.split(":")[0] for doc in docs_rubrique)
    docs_titre = set(doc.split(":")[0] for doc in docs_titre)
    docs_contenu = set(doc.split(":")[0] for doc in docs_contenu)
    docs_keywords = set(doc.split(":")[0] for doc in docs_keywords)
    docs_image = set(doc.split(":")[0] for doc in docs_image)

    docs_possibles = []
    for required in liste_required:
        if required == "date":
            docs_possibles.append(docs_date)
        elif required == "rubrique":
            docs_possibles.append(docs_rubrique)
        elif required == "titre":
            docs_possibles.append(docs_titre)
        elif required == "contenu":
            docs_possibles.append(docs_contenu)
        elif required == "keywords":
            docs_possibles.append(docs_keywords)
        elif required == "image":
            docs_possibles.append(docs_image)

    print(f"Docs sur keywords : {docs_keywords}")
    print(f"Docs non keywords : {docs_non_keywords}")
    print(f"Docs sur titre : {docs_titre}")
    print(f"Docs sur contenu : {docs_contenu}")
    print(f"Docs sur date : {docs_date}")
    print(f"Docs sur rubrique : {docs_rubrique}")
    print(f"Docs sur image : {docs_image}")
    print(docs_possibles)
    if not docs_possibles:
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

    if composants["doc_type"] == "rubrique":
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

    if composants["doc_type"] == "bulletin":
        resultat = []
        for article in final_intersect:
            mask = df.apply(
                lambda ligne: f"{article}:numero" in map(str, ligne.values), axis=1
            )
            match = df.loc[mask, 0]
            if not match.empty:
                resultat.append(match.iloc[0])
        return set(resultat), composants["doc_type"]
    return set(), "article"


if __name__ == "__main__":
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
        "Quels articles évoquent la ville de Grenoble ?",
        "Articles parlant de drones.",
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

    for queri in queries:
        moteur(queri)
