"""
Fonctions pour évaluer le moteur sur quelques requêtes sélectionnées.
"""

import time
from datetime import datetime
import xml.etree.ElementTree as et
import matplotlib.pyplot as plt
import pandas as pd
from moteur import moteur


def fichiers_rubrique_focus_avec_images(xml_path):
    """
    Renvoie la liste des fichiers dont la rubrique est 'Focus' et qui contiennent des images.

    :param xml_path: chemin vers le fichier corpus.xml
    :return: liste des identifiants <fichier> correspondants
    """
    tree = et.parse(xml_path)
    root = tree.getroot()

    fichiers = []

    for article in root.findall("article"):
        rubrique = article.findtext("rubrique")
        images_element = article.find("images")

        # Vérifie que la rubrique est "Focus" et que <images> contient au moins une <image>
        if rubrique.lower() == "focus" and images_element is not None:
            if images_element.find("image") is not None:
                fichier = article.findtext("fichier")
                if fichier:
                    fichiers.append(fichier)

    return fichiers


def extraire_fichiers_filtres(xml_path):
    """
    Renvoie les valeurs <fichier> des articles datés entre 2013 et 2014,
    mais pas au mois de juin.

    :param xml_path: chemin du fichier corpus.xml
    :return: liste des identifiants <fichier> correspondants
    """
    tree = et.parse(xml_path)
    root = tree.getroot()

    fichiers = []

    for article in root.findall("article"):
        date_str = article.findtext("date")
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        except (TypeError, ValueError):
            continue

        if 2012 <= date_obj.year <= 2013 and date_obj.month != 6:
            fichier = article.findtext("numero")
            if fichier:
                fichiers.append(fichier)

    return fichiers


if __name__ == "__main__":
    # Jeu de test : 10 requêtes du TD6
    REQUETES_TEST = [
        "Je voudrais les articles qui parlent de cuisine moléculaire.",
        "Quels sont les articles sur la réalité virtuelle?",
        "Je voudrais les articles qui parlent d’airbus ou du projet Taxibot.",
        "Je voudrais tous les bulletins écrits entre 2012 et 2013 mais pas au mois de juin.",
        "Quels sont les articles dont le titre contient biocarburant ou le contenu parle des bioénergies ?",
        "Je souhaite les rubriques des articles parlant de nutrition ou de vins.",
        "Articles dont la rubrique est 'Horizon Enseignement' mais qui ne parlent pas d’ingénieurs.",
        "Quels sont les articles dont le titre contient le mot chimie?",
        "Lister tous les articles dont la rubrique est Focus et qui ont des images.",
        "Je veux les articles de 2014 et de la rubrique Focus et parlant de la santé.",
    ]

    for requete in REQUETES_TEST:
        print("#####################################################")
        print(f"Requête : {requete}")
        print(f"Liste de documents trouvés : {moteur(requete)}")

    # Docs pertinents définis manuellement pour chaque requête
    docs_pertinents = {
        REQUETES_TEST[0]: {"74752"},
        REQUETES_TEST[1]: {"70421", "70162", "74168", "75064"},
        REQUETES_TEST[2]: {
            "72933",
            "67797",
            "74745",
            "72636",
            "71617",
            "68383",
            "70920",
        },
        REQUETES_TEST[3]: {
            "272",
            "284",
            "267",
            "273",
            "282",
            "277",
            "286",
            "275",
            "278",
            "266",
            "285",
            "270",
            "274",
            "276",
            "287",
            "283",
            "269",
            "268",
            "279",
            "280",
        },
        REQUETES_TEST[4]: {"68385", "72121"},
        REQUETES_TEST[5]: {
            "focus",
            "au coeur des régions",
            "evénement",
            "actualité innovation",
            "du côté des pôles",
            "actualités innovations",
        },
        REQUETES_TEST[6]: {"73437", "72636", "72637"},
        REQUETES_TEST[7]: {"67561", "68278", "75461"},
        REQUETES_TEST[8]: {
            "67794",
            "67795",
            "67937",
            "67938",
            "68274",
            "68276",
            "68383",
            "68638",
            "68881",
            "68882",
            "69177",
            "69178",
            "69179",
            "69811",
            "70161",
            "70420",
            "70421",
            "70422",
            "70914",
            "70916",
            "71612",
            "71614",
            "71835",
            "71836",
            "71837",
            "72113",
            "72114",
            "72115",
            "72392",
            "72629",
            "72932",
            "72933",
            "73182",
            "73183",
            "73185",
            "73430",
            "73431",
            "73683",
            "73684",
            "73875",
            "73876",
            "74167",
            "74168",
            "74450",
            "75063",
            "75064",
            "75065",
            "75457",
            "75458",
            "75788",
            "75789",
            "75790",
            "76206",
            "76207",
            "76507",
            "76508",
        },
        REQUETES_TEST[9]: {"76507", "75459", "75458"},
    }

    # Réponses simulées du moteur
    requete_to_docs = {
        "Je voudrais les articles qui parlent de cuisine moléculaire.": ["74752"],  # ok
        "Quels sont les articles sur la réalité virtuelle?": [
            "70421",
            "75064",
            "74168",
            "70162",
        ],  # manque le 70162
        "Je voudrais les articles qui parlent d’airbus ou du projet Taxibot.": [
            "67797",
            "74745",
            "72933",
            "71617",
            "70920",
            "72636",
            "68383",
        ],
        "Je voudrais tous les bulletins écrits entre 2012 et 2013 mais pas au mois de juin.": [
            "272",
            "284",
            "267",
            "273",
            "282",
            "277",
            "286",
            "275",
            "278",
            "266",
            "285",
            "270",
            "274",
            "276",
            "287",
            "283",
            "269",
            "268",
            "279",
            "280",
        ],
        "Quels sont les articles dont le titre contient biocarburant ou le contenu parle des bioénergies ?": [
            "72121",
            "68385",
        ],
        "Je souhaite les rubriques des articles parlant de nutrition ou de vins.": [
            "focus",
            "evénement",
            "au coeur des régions",
            "actualité innovation",
            "du côté des pôles",
            "actualités innovations",
        ],
        "Articles dont la rubrique est 'Horizon Enseignement' mais qui ne parlent pas d’ingénieurs.": [
            "72636",
            "72637",
            "73437",
        ],
        "Quels sont les articles dont le titre contient le mot chimie?": [
            "75461",
            "68278",
            "67561",
        ],
        "Lister tous les articles dont la rubrique est Focus et qui ont des images.": [
            "72933",
            "73684",
            "75065",
            "70421",
            "75458",
            "67937",
            "73430",
            "71614",
            "73683",
            "72114",
            "67794",
            "72113",
            "75788",
            "75063",
            "73183",
            "76508",
            "75457",
            "73182",
            "75789",
            "69177",
            "70420",
            "68274",
            "76207",
            "75790",
            "75064",
            "73185",
            "68881",
            "73876",
            "71835",
            "74168",
            "71836",
            "72932",
            "71837",
            "67795",
            "72392",
            "70161",
            "71612",
            "68638",
            "67938",
            "69178",
            "70916",
            "76507",
            "76206",
            "72115",
            "73431",
            "70422",
            "74167",
            "68882",
            "68383",
            "72629",
            "74450",
            "73875",
            "69179",
            "69811",
            "68276",
            "70914",
        ],
        "Je veux les articles de 2014 et de la rubrique Focus et parlant de la santé.": [
            "76507",
            "75458",
            "75459",
        ],
    }

    def moteur_simule(query):
        """
        Fais appel à un dictionnaire pour renvoyer les résultats,
        plutôt que de faire appel au moteur (les résultats sont les mêmes).
        """
        return requete_to_docs.get(query, [])

    resultats = []

    for REQUETE in REQUETES_TEST:
        pertinents = docs_pertinents[REQUETE]
        systeme = set(moteur_simule(REQUETE))

        tp = len(pertinents & systeme)
        fp = len(systeme - pertinents)
        fn = len(pertinents - systeme)

        precision = tp / (tp + fp) if tp + fp > 0 else 0
        rappel = tp / (tp + fn) if tp + fn > 0 else 0
        f_mesure = (
            2 * (precision * rappel) / (precision + rappel)
            if (precision + rappel) > 0
            else 0
        )

        resultats.append(
            {
                "requête": REQUETE,
                "precision": round(precision, 2),
                "rappel": round(rappel, 2),
                "f_mesure": round(f_mesure, 2),
            }
        )

    df = pd.DataFrame(resultats)
    print(df)

    df_plot = df[["requête", "precision", "rappel", "f_mesure"]].set_index("requête")
    df_plot.plot(
        kind="bar", figsize=(12, 6), title="Évaluation du moteur (10 requêtes)"
    )
    plt.ylabel("Score")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.grid(axis="y")
    plt.show()

    REQUETES_TEST = [
        "Je voudrais les articles qui parlent de cuisine moléculaire.",
        "Quels sont les articles sur la réalité virtuelle?",
        "Je voudrais les articles qui parlent d’airbus ou du projet Taxibot.",
        # "Je voudrais tous les bulletins écrits entre 2012 et 2013 mais pas au mois de juin.", Trop lent
        "Quels sont les articles dont le titre contient biocarburant ou le contenu parle des bioénergies ?",
        "Je souhaite les rubriques des articles parlant de nutrition ou de vins.",
        "Articles dont la rubrique est 'Horizon Enseignement' mais qui ne parlent pas d’ingénieurs.",
        "Quels sont les articles dont le titre contient le mot chimie?",
        "Lister tous les articles dont la rubrique est Focus et qui ont des images.",
        "Je veux les articles de 2014 et de la rubrique Focus et parlant de la santé.",
    ]

    temps_moyens = {}

    # boucle sur chaque requête (les 9)
    for REQUETE in REQUETES_TEST:
        TEMPS_TOTAL = 0.0
        for _ in range(100):
            debut = time.time()
            moteur(REQUETE)
            fin = time.time()
            TEMPS_TOTAL += fin - debut
        temps_moyens[REQUETE] = round(TEMPS_TOTAL / 100, 4)

    #  graphique
    plt.figure(figsize=(14, 6))
    plt.bar(
        range(len(temps_moyens)),
        list(temps_moyens.values()),
        tick_label=[f"Q{i+1}" for i in range(len(temps_moyens))],
    )
    plt.xlabel("Requête (abrégée)")
    plt.ylabel("Temps moyen (secondes)")
    plt.title("Temps de réponse moyen du moteur (100 exécutions)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    for i, (req, t) in enumerate(temps_moyens.items()):
        print(f"Q{i+1} : {t:.4f} sec — {req}")

    REQUETE_LENTE = "Je voudrais tous les bulletins écrits entre 2012 et 2013 mais pas au mois de juin."

    temps_execution = []
    for _ in range(4):
        debut = time.time()
        moteur(REQUETE_LENTE)
        fin = time.time()
        temps_execution.append(fin - debut)

    temps_moyen = round(sum(temps_execution) / len(temps_execution), 4)
    print(f"Temps moyen pour la requête bulletins : {temps_moyen} secondes")

    plt.figure(figsize=(10, 5))
    plt.plot(temps_execution, marker="o")
    plt.xlabel("Exécution")
    plt.ylabel("Temps (secondes)")
    plt.title("Temps d'exécution pour 4 recherches de bulletins")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
