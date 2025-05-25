"""
Fichier permettant la constitution d'un anti-dictionnaire et le nettoyage du corpus initial.
"""

import math
from typing import List
import pandas as pd
from lxml import etree
from tqdm import tqdm
from segmente import tokenize
from substitue import substitue_texte


def tf_determination(fichier_segmentation: str, fichier_tf: str) -> None:
    """
    Calcule les valeurs TF (Term Frequency) pour chaque terme du corpus
    et les sauvegarde dans un fichier.

    :param fichier_segmentation: Le chemin du fichier contenant les paires (tokens/n° de fichier).
    :param fichier_tf: Le chemin du fichier où les valeurs TF doivent être enregistrées.
    :return: None
    """
    segmentation_df = pd.read_csv(
        fichier_segmentation, sep="\t", header=None, names=["word", "file_number"]
    )

    # Liste des différents numéros fichiers dans le corpus
    liste_fichiers_uniques = segmentation_df["file_number"].unique()

    with open(fichier_tf, "w", encoding="utf-8") as file:
        for num_fichier in liste_fichiers_uniques:
            # Extraction des mots du fichier actuel
            df_fichier = segmentation_df[segmentation_df["file_number"] == num_fichier]
            compte_mot = df_fichier[
                "word"
            ].value_counts()  # Comptage des occurrences des mots
            frequence_mot = compte_mot / len(
                df_fichier
            )  # Calcul de la fréquence des mots (TF)

            # Enregistrement des résultats au format (numéro de fichier, mot, TF)
            for mot, frequence in frequence_mot.items():
                file.write(f"{num_fichier}\t{mot}\t{frequence}\n")


def idf_determination(fichier_tf: str, fichier_idf: str) -> None:
    """
    Calcule les valeurs idf (inverse document frequency) pour chaque terme du corpus
    et les sauvegarde dans un fichier.

    :param fichier_tf: Le chemin du fichier contenant les valeurs tf (term frequency)
    par mot et par fichier.
    :param fichier_idf: Le chemin du fichier où les valeurs idf doivent être enregistrées.
    :return: None
    """
    tf_dataframe = pd.read_csv(
        fichier_tf, sep="\t", header=None, names=["file_number", "word", "tf"]
    )

    # Nombre total de documents dans le corpus
    n = len(tf_dataframe["file_number"].unique())

    with open(fichier_idf, "w", encoding="utf-8") as file:
        mots = tf_dataframe["word"].unique()
        # Calcul du df et idf pour chaque mot
        for mot in mots:
            # Calcul du df (document frequency) : nb de documents contenant le mot
            df = len(tf_dataframe[tf_dataframe["word"] == mot])
            # Calcul du idf
            idf = math.log10(n / df)
            # Écriture du mot et de son idf dans le fichier de sortie
            file.write(f"{mot}\t{idf}\n")


def calcul_tf_idf(fichier_tf: str, fichier_idf: str, fichier_tfidf: str) -> None:
    """
    Calcule les valeurs tf-idf pour chaque terme du corpus et les sauvegarde dans un fichier.

    :param fichier_tf: Le fichier contenant les valeurs tf pour chaque mot.
    :param fichier_idf: Le fichier contenant les valeurs idf pour chaque mot.
    :param fichier_tfidf: Le fichier de sortie pour enregistrer les valeurs tf-idf.
    :return: None
    """
    # Lecture des fichiers tf et idf - format pandas
    tf_dataframe = pd.read_csv(
        fichier_tf, sep="\t", header=None, names=["file_number", "word", "tf"]
    )
    idf_dataframe = pd.read_csv(
        fichier_idf, sep="\t", header=None, names=["word", "idf"]
    )

    # Fusion des deux dataframes sur la colonne 'word'
    dataframe_joint = pd.merge(tf_dataframe, idf_dataframe, on="word")
    # Calcul de tf-idf = tf*idf
    dataframe_joint["tfidf"] = dataframe_joint["tf"] * dataframe_joint["idf"]

    # Tri des résultats par tf-idf (by=['file_number','tfidf', 'word'] si on veut par fichier)
    tf_idf_dataframe = dataframe_joint.drop(columns=["tf", "idf"])
    tf_idf_dataframe.sort_values(by=["tfidf", "word"], inplace=True)

    tf_idf_dataframe.to_csv(fichier_tfidf, sep="\t", index=False, header=False)


def definition_stop_words(
    fichier_tfidf: str, fichier_subs: str, seuil_min: float
) -> List[str]:
    """
    Crée un anti-dictionnaire en supprimant les termes ayant un tf-idf inférieur à un seuil minimum.

    :param fichier_tfidf: Le fichier contenant les valeurs tf-idf.
    :param fichier_subs: Le fichier contenant les mots à substituer.
    :param seuil_min: Le seuil minimum de tf-idf au-dessous duquel les mots sont
    considérés comme non pertinents.
    :return: La liste des mots considérés comme stop words.
    """
    # Lecture des fichiers tf-idf et de substitution
    tfidf_dataframe = pd.read_csv(
        fichier_tfidf, sep="\t", header=None, names=["file_number", "word", "tfidf"]
    )

    # Calcul de la moyenne du tf-idf pour chaque mot
    moyenne_tfidf = tfidf_dataframe.groupby("word")["tfidf"].mean()
    # Sélection des mots ayant une moyenne de tf-idf inférieure au seuil
    stop_words = moyenne_tfidf[moyenne_tfidf < seuil_min].index.tolist()
    # Écriture des stop words dans le fichier de substitution
    with open(fichier_subs, "w", encoding="utf-8") as file:
        for word in stop_words:
            file.write(f"{word}\t\n")

    return stop_words


def nettoyage_corpus_xml(
    corpus_entree: str, fichier_subs: str, corpus_sortie: str
) -> None:
    """
    Nettoie le corpus XML en appliquant des substitutions de mots sur les titres et textes.

    :param corpus_entree: Le chemin du fichier XML d'entrée
    :param fichier_subs: Le fichier contenant les substitutions de mots
    :param corpus_sortie: Le chemin du fichier XML de sortie
    :return: None
    """
    # Charge le fichier XML d'entrée et crée une copie
    tree = etree.parse(corpus_entree)

    for article in tqdm(tree.xpath("/corpus/article")):
        # Tokenise le titre et applique les substitutions
        titre = substitue_texte(tokenize(article.find("titre").text), fichier_subs)
        # .split() permet de retirer des espaces consécutifs
        article.find("titre").text = " ".join(titre.split())

        # Tokenise le texte et applique les substitutions
        texte = substitue_texte(tokenize(article.find("texte").text), fichier_subs)
        # .split() permet de retirer des espaces consécutifs
        article.find("texte").text = " ".join(texte.split())

    # Enregistre le fichier XML
    tree.write(corpus_sortie, pretty_print=True, xml_declaration=True, encoding="UTF-8")


if __name__ == "__main__":
    print("Calcul de TF...")
    tf_determination("data/words_segmentation.txt", "data/TF_output.txt")
    print("Calcul du IDF...")
    idf_determination("data/TF_output.txt", "data/idf_output.txt")
    print("Calcul de TF-IDF...")
    calcul_tf_idf("data/TF_output.txt", "data/idf_output.txt", "data/tfidf_output.txt")
    print("Génération de l'anti-dictionnaire...")
    definition_stop_words("data/tfidf_output.txt", "data/subs.txt", 0.0006)
    print("Nettoyage du corpus...")
    nettoyage_corpus_xml(
        "data/corpus.xml", "data/subs.txt", "data/corpus_wo_stopwords.xml"
    )
