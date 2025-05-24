"""
Fonction principale qui permet la recherche d'information à partir d'une requête.
"""

import re
from datetime import datetime
from typing import Tuple, Optional
import pandas as pd
from requetes import nettoyage_requete, traitement_requete, replace_soit
from correcteur import correcteur_orthographique
from utils import get_min_max_dates, replace_min_and_max


def charger_index(index: str = "data/index_inverse.txt") -> pd.DataFrame:
    """
    Charge l'index inversé et le met sous forme de dataframe pandas.
    :param index: Le chemin vers l'index inversé.
    :return: Le dataframe pandas.
    """
    with open(index, "r", encoding="utf-8") as f:
        lines = [line.strip().split(",") for line in f.readlines()]

    return pd.DataFrame(lines)


def corriger_texte(texte: str) -> str:
    """
    Applique le correcteur orthographique sur un texte.
    :param texte: Le texte à corriger.
    :return: Le texte corrigé.
    """
    return correcteur_orthographique(texte, "data/lemma_stemmer.txt", 1, 12, 54).strip()


def filtrer_par(field: str, docs_set: set[str]) -> None:
    """
    Modifie un set de docs:champ en ne conservant que ceux pour lesquels champ=field.
    :param field: Le champ sur lequel filtrer.
    :param docs_set: Le set à filtrer.
    :return: None.
    """
    docs_set.intersection_update({
        doc for doc in docs_set
        if ":" in doc and doc.split(":")[1].strip() == field
    })


def moteur(requete: str) -> Tuple[Optional[set], str]:
    """
    Moteur de recherche de la base d'information de l'ADIT.
    Il reçoit en entrée une requête, la traite, la transforme en requête structurée
    puis parcourt l'index inversé intelligemment pour renvoyer les résultats.
    :param requete: La requête à traiter.
    :return: Un tuple (set de résultats, type de doc à retourner)
    """

    # chargement de l'index inversé sous forme de dataframe
    df = charger_index()

    liste_champs_requis = []

    tous_docs = df.iloc[:, 1:].values.flatten().tolist()
    tous_docs = [doc for doc in tous_docs if doc is not None and pd.notna(doc)]
    tous_docs = set(tous_docs)

    docs_date = set()
    dates_liste = set()
    docs_rubrique = set()
    docs_titre = tous_docs.copy()
    docs_contenu = set()
    docs_non_keywords = tous_docs.copy()
    docs_keywords = tous_docs.copy()
    docs_image = set()

    # Correction et traitement des requêtes
    composants = traitement_requete(nettoyage_requete(replace_soit(requete)))
    print(composants)
    if composants["titre"] is not None:
        composants["titre"] = corriger_texte(composants["titre"])
    if composants["contenu"] is not None:
        composants["contenu"] = corriger_texte(composants["contenu"])
    if composants["keywords"] is not None:
        for mot in composants["keywords"]:
            if mot == "ou":
                continue
            if not mot.startswith("pas "):
                composants["keywords"][composants["keywords"].index(mot)] = (
                    corriger_texte(mot)
                )
            else:
                composants["keywords"][composants["keywords"].index(mot)] = (
                    "pas " + corriger_texte(mot[4:])
                )

    # Docs date
    if composants["date"] is not None:
        liste_champs_requis.append("date")
        if "exact" in composants["date"]:
            date = composants["date"]["exact"]
            composants["date"]["min"], composants["date"]["max"] = get_min_max_dates(
                date
            )
            del composants["date"]["exact"]
        replace_min_and_max(composants["date"])
        if "min" in composants["date"] and "max" in composants["date"]:
            for valeur in df[0]:
                try:
                    date_valeur = datetime.strptime(valeur, "%d/%m/%Y")
                    date_min = datetime.strptime(composants["date"]["min"], "%d/%m/%Y")
                    date_max = datetime.strptime(composants["date"]["max"], "%d/%m/%Y")
                    if date_min <= date_valeur <= date_max:
                        dates_liste.add(valeur)
                except ValueError:
                    pass

        elif "min" in composants["date"]:
            for valeur in df[0]:
                try:
                    date_valeur = datetime.strptime(valeur, "%d/%m/%Y")
                    date_min = datetime.strptime(composants["date"]["min"], "%d/%m/%Y")
                    if date_min <= date_valeur:
                        dates_liste.add(valeur)
                except ValueError:
                    pass
        elif "max" in composants["date"]:
            for valeur in df[0]:
                try:
                    date_valeur = datetime.strptime(valeur, "%d/%m/%Y")
                    date_max = datetime.strptime(composants["date"]["max"], "%d/%m/%Y")
                    if date_valeur <= date_max:
                        dates_liste.add(valeur)
                except ValueError:
                    pass
        if "pas" in composants["date"]:
            pas_pattern = composants["date"]["pas"]
            pas_pattern = pas_pattern.replace("****", ".*")
            pas_pattern = pas_pattern.replace("**", ".*")
            annee = pas_pattern[0:2]
            mois = pas_pattern[3:5]
            jour = pas_pattern[6:8]
            pas_pattern = f"{jour}/{mois}/{annee}"
            dates_filtre = set(
                d for d in dates_liste if not re.fullmatch(pas_pattern, d)
            )
        else:
            dates_filtre = dates_liste

        for date in dates_filtre:
            docs_date.update(df[df[0] == date].iloc[:, 1:].values.flatten().tolist())

    docs_date = set(doc for doc in docs_date if doc is not None and pd.notna(doc))
    filtrer_par("date", docs_date)

    # Docs rubrique
    dico_rubriques = {
        "focus": "focus",
        "au coeur regions": "au coeur des régions",
        "evenement": "evénement",
        "evénement": "evénement",
        "événement": "evénement",
        "actualité innovation": "actualité innovation",
        "actualités innovation": "actualités innovation",
        "actualités innovations": "actualités innovations",
        "direct laboratoires": "en direct des laboratoires",
        "direct labos": "en direct des labos",
        "a lire": "a lire",
        "horizon enseignement": "horizon enseignement",
        "horizons enseignement": "horizons enseignement",
        "horizons formation enseignement": "horizon formation enseignement",
        "horizon formation": "horizon formation",
        "côté pôles": "du côté des pôles",
    }

    if composants["rubriques"] is not None and composants["rubriques"]:
        liste_champs_requis.append("rubrique")
        for rubrique in composants["rubriques"]:
            docs_rubrique.update(
                df[df[0] == dico_rubriques[rubrique]]
                .iloc[:, 1:]
                .values.flatten()
                .tolist()
            )
    docs_rubrique = set(
        doc for doc in docs_rubrique if doc is not None and pd.notna(doc)
    )
    filtrer_par("rubrique", docs_rubrique)

    # Docs titre
    if composants["titre"] is not None:
        liste_champs_requis.append("titre")
        titre_propre = composants["titre"].strip()  # retire les espaces en trop
        for mot in titre_propre.split(" "):
            docs_titre &= set(df[df[0] == mot].iloc[:, 1:].values.flatten().tolist())

    docs_titre = set(doc for doc in docs_titre if doc and pd.notna(doc))
    filtrer_par("titre", docs_titre)

    # Docs contenu
    if composants["contenu"] is not None:
        liste_champs_requis.append("contenu")
        contenu_propre = composants["contenu"].strip()
        docs_contenu = (
            df[df[0] == contenu_propre].iloc[:, 1:].values.flatten().tolist()
        )

    docs_contenu = set(doc for doc in docs_contenu if doc and pd.notna(doc))
    filtrer_par("texte", docs_contenu)

    # Docs keywords négatifs
    pas_keywords_remove = None
    if composants["keywords"]:
        liste_champs_requis.append("keywords")
        for keyword in composants["keywords"]:
            if keyword.startswith("pas "):
                pas_keywords_remove = keyword
                pas_keywords = keyword.split()
                pas_keywords = pas_keywords[1:]

                for pas_keyword in pas_keywords:
                    docs_non_keywords &= set(
                        df[df[0] == pas_keyword].iloc[:, 1:].values.flatten().tolist()
                    )

    docs_non_keywords = set(
        doc for doc in docs_non_keywords
        if doc.split(":")[1] in ("texte", "titre")
    )

    if pas_keywords_remove is not None:
        composants["keywords"].remove(pas_keywords_remove)
    else:
        docs_non_keywords = set()

    # Si le mot 'ou' est resté seul dans les keywords, on renvoie un OU
    # sur le titre et le contenu
    if len(composants["keywords"]) == 1 and composants["keywords"][0] == "ou":
        doc_retourne = set(docs_titre) | set(docs_contenu)
        return doc_retourne, composants["doc_type"]

    # S'il y a un OU dans les keywords, on prend tout ce qu'il y a avant
    # et l'on fait la disjonction avec ce qu'il y a après
    if "ou" in composants["keywords"]:
        liste_ou = composants["keywords"].index("ou")
        liste_ou1 = composants["keywords"][:liste_ou]
        liste_ou2 = composants["keywords"][liste_ou + 1 :]
        docs_liste1 = tous_docs.copy()
        docs_liste2 = tous_docs.copy()

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
        for keyword in composants["keywords"]:
            docs_keywords &= set(
                df[df[0] == keyword].iloc[:, 1:].values.flatten().tolist()
            )

    if composants["image"] is not None:
        liste_champs_requis.append("images")
        if composants["image"] == 1:
            docs_image.update(
                df[df[0] == "presence_image"].iloc[:, 1:].values.flatten().tolist()
            )
        else:
            docs_image.update(df[df[0] == "pas_image"].iloc[:, 1:].values.flatten().tolist())
    docs_image = set(doc for doc in docs_image if doc is not None and pd.notna(doc))

    # On récupère seulement les n° de fichiers et pas le champ associé
    docs_date = set(doc.split(":")[0] for doc in docs_date)
    docs_rubrique = set(doc.split(":")[0] for doc in docs_rubrique)
    docs_titre = set(doc.split(":")[0] for doc in docs_titre)
    docs_contenu = set(doc.split(":")[0] for doc in docs_contenu)
    docs_keywords = set(doc.split(":")[0] for doc in docs_keywords)
    docs_non_keywords = set(doc.split(":")[0] for doc in docs_non_keywords)
    docs_image = set(doc.split(":")[0] for doc in docs_image)

    # On prépare l'intersection des documents seulement sur les champs qui étaient requis
    # (sinon on renverrait tout le temps des sets vides
    # car l'intersection avec un set vide est un set vide)
    docs_possibles = []
    for champ_requis in liste_champs_requis:
        if champ_requis == "date":
            docs_possibles.append(docs_date)
        elif champ_requis == "rubrique":
            docs_possibles.append(docs_rubrique)
        elif champ_requis == "titre":
            docs_possibles.append(docs_titre)
        elif champ_requis == "contenu":
            docs_possibles.append(docs_contenu)
        elif champ_requis == "keywords":
            docs_possibles.append(docs_keywords)
        elif champ_requis == "images":
            docs_possibles.append(docs_image)

    print(f"Docs sur keywords : {docs_keywords}")
    print(f"Docs non keywords : {docs_non_keywords}")
    print(f"Docs sur titre : {docs_titre}")
    print(f"Docs sur contenu : {docs_contenu}")
    print(f"Docs sur date : {docs_date}")
    print(f"Docs sur rubrique : {docs_rubrique}")
    print(f"Docs sur image : {docs_image}")

    if not docs_possibles:
        return None, composants["doc_type"]
    intersect = set.intersection(*docs_possibles)

    # Nettoyer et filtrer l'intersection
    # On enlève les docs correspondant aux "pas keywords"
    intersect = {doc.strip() for doc in intersect}
    intersect -= docs_non_keywords

    # Traitement des différents cas de retour (article ou bulletin ou rubrique)
    if composants["doc_type"] == "article":
        return intersect, composants["doc_type"]

    df_str = df.astype(str).map(str.strip)
    col0 = df_str.iloc[:, 0]
    if composants["doc_type"] == "rubrique":
        motifs = [f"{article}:rubrique" for article in intersect]
        mask = df_str.apply(lambda row: any(motif in row.values for motif in motifs), axis=1)
        resultat = col0[mask].str.strip().unique()
        return set(resultat), composants["doc_type"]

    if composants["doc_type"] == "bulletin":
        motifs = [f"{article}:numero" for article in intersect]
        mask = df_str.apply(lambda row: any(motif in row.values for motif in motifs), axis=1)
        resultat = col0[mask].unique()
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
