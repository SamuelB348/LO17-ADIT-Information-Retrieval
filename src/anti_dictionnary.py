"""
Fichier permettant la constitution d'un anti-dictionnaire et le nettoyage du corpus initial.
"""

import math
from typing import List
import pandas as pd
from xml.dom import minidom
import xml.etree.ElementTree as ET
from lxml import etree
from segmente import tokenize
from substitue import substitute_texte


def tf_determination(segmentation_file: str, output_tf_file: str) -> None:
    """
    Calcule les valeurs TF (Term Frequency) pour chaque terme du corpus
    et les sauvegarde dans un fichier.

    :param segmentation_file: Le chemin du fichier contenant les paires (tokens/n° de fichier).
    :param output_tf_file: Le chemin du fichier où les valeurs TF doivent être enregistrées.
    :return: None
    """
    segmentation_df = pd.read_csv(
        segmentation_file, sep="\t", header=None, names=["word", "file_number"]
    )

    # Liste des différents numéros fichiers dans le corpus
    liste_different_files = segmentation_df["file_number"].unique()

    with open(output_tf_file, "w", encoding="utf-8") as file:
        for file_number in liste_different_files:
            # Extraction des mots du fichier actuel
            file_df = segmentation_df[segmentation_df["file_number"] == file_number]
            word_counts = file_df["word"].value_counts()  # Comptage des occurrences des mots
            word_frequency = word_counts / len(file_df)  # Calcul de la fréquence des mots (TF)

            # Enregistrement des résultats au format (numéro de fichier, mot, TF)
            for word, frequency in word_frequency.items():
                file.write(f"{file_number}\t{word}\t{frequency}\n")


def idf_determination(input_tf_file: str, output_idf_file: str) -> None:
    """
    Calcule les valeurs idf (inverse document frequency) pour chaque terme du corpus
    et les sauvegarde dans un fichier.

    :param input_tf_file: Le chemin du fichier contenant les valeurs tf (term frequency)
    par mot et par fichier.
    :param output_idf_file: Le chemin du fichier où les valeurs idf doivent être enregistrées.
    :return: None
    """
    tf_dataframe = pd.read_csv(
        input_tf_file, sep="\t", header=None, names=["file_number", "word", "tf"]
    )

    # Nombre total de documents dans le corpus
    n = len(tf_dataframe["file_number"].unique())

    with open(output_idf_file, "w", encoding="utf-8") as file:
        words = tf_dataframe["word"].unique()
        # Calcul du df et idf pour chaque mot
        for word in words:
            # Calcul du df (document frequency) : nb de documents contenant le mot
            df = len(tf_dataframe[tf_dataframe["word"] == word])
            # Calcul du idf
            idf = math.log10(n / df)
            # Écriture du mot et de son idf dans le fichier de sortie
            file.write(f"{word}\t{idf}\n")


def compute_tf_idf(
    input_tf_file: str, input_idf_file: str, output_tfidf_file: str
) -> None:
    """
    Calcule les valeurs tf-idf pour chaque terme du corpus et les sauvegarde dans un fichier.

    :param input_tf_file: Le fichier contenant les valeurs tf pour chaque mot.
    :param input_idf_file: Le fichier contenant les valeurs idf pour chaque mot.
    :param output_tfidf_file: Le fichier de sortie pour enregistrer les valeurs tf-idf.
    :return: None
    """
    # Lecture des fichiers tf et idf - format pandas
    tf_dataframe = pd.read_csv(
        input_tf_file, sep="\t", header=None, names=["file_number", "word", "tf"]
    )
    idf_dataframe = pd.read_csv(
        input_idf_file, sep="\t", header=None, names=["word", "idf"]
    )

    # Fusion des deux dataframes sur la colonne 'word'
    merged_dataframe = pd.merge(tf_dataframe, idf_dataframe, on="word")
    # Calcul de tf-idf = tf*idf
    merged_dataframe["tfidf"] = merged_dataframe["tf"] * merged_dataframe["idf"]

    # Tri des résultats par tf-idf (by=['file_number','tfidf', 'word'] si on veut par fichier)
    tf_idf_dataframe = merged_dataframe.drop(columns=["tf", "idf"])
    tf_idf_dataframe.sort_values(by=["tfidf", "word"], inplace=True)

    tf_idf_dataframe.to_csv(output_tfidf_file, sep="\t", index=False, header=False)


def create_stop_words(input_tfidf_file: str, subs_file: str, seuil_min: float) -> List[str]:
    """
    Crée un anti-dictionnaire en supprimant les termes ayant un tf-idf inférieur à un seuil minimum.

    :param input_tfidf_file: Le fichier contenant les valeurs tf-idf.
    :param subs_file: Le fichier contenant les mots à substituer.
    :param seuil_min: Le seuil minimum de tf-idf au-dessous duquel les mots sont
    considérés comme non pertinents.
    :return: La liste des mots considérés comme stop words.
    """
    # Lecture des fichiers tf-idf et de substitution
    tfidf_dataframe = pd.read_csv(
        input_tfidf_file, sep="\t", header=None, names=["file_number", "word", "tfidf"]
    )

    # Sélection des mots ayant un tf-idf inférieur au seuil minimum
    stop_words = tfidf_dataframe[tfidf_dataframe["tfidf"] < seuil_min]["word"].unique()
    # Écriture dans le fichier subs_file
    with open(subs_file, "w", encoding="utf-8") as file:
        for word in stop_words:
            file.write(f"{word}\t{''}\n")
    return stop_words


def create_clean_xml_corpus(
    input_corpus: str, subs_file: str, output_corpus: str
) -> None:
    """
    Nettoie le corpus XML en appliquant des substitutions de mots sur les titres et textes.

    :param input_corpus: Le chemin du fichier XML d'entrée
    :param subs_file: Le fichier contenant les substitutions de mots
    :param output_corpus: Le chemin du fichier XML de sortie
    :return: None
    """
    # Charge le fichier XML d'entrée et crée une copie
    tree = etree.parse(input_corpus)

    for article in tree.xpath("/corpus/article"):
        # Tokenise le titre et applique les substitutions
        titre = tokenize(article.find("titre").text)
        titre = substitute_texte(titre, subs_file)
        article.find("titre").text = "".join(titre)

        # Tokenise le texte et applique les substitutions
        texte = tokenize(article.find("texte").text)
        texte = substitute_texte(texte, subs_file)
        article.find("texte").text = "".join(texte)

    # Enregistre le fichier XML
    tree.write(
        output_corpus,
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8"
    )


if __name__ == "__main__":
    # tf_determination("../words_segmentation.txt", "../TF_output.txt")
    # idf_determination("../TF_output.txt", "../idf_output.txt")
    # compute_tf_idf("../TF_output.txt", "../idf_output.txt", "../tfidf_output.txt")
    # create_stop_words("../tfidf_output.txt", "../subs.txt", 0.0006)
    create_clean_xml_corpus("../corpus.xml", "../subs.txt", "../corpus_wo_stopwords.xml")
