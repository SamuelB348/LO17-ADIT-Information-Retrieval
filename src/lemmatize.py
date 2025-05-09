"""
Fonctions pour lemmatiser le corpus selon différentes approches.
"""

import re
import spacy
import pandas as pd
from nltk.stem.snowball import FrenchStemmer
from lxml import etree
from anti_dictionnary import create_clean_xml_corpus
from utils import tokenize


def extract_words_from_xml(input_xml_file: str, output_file: str) -> None:
    """
    Extrait les mots des balises <titre> et <texte> d'un fichier xml, les normalise simplement,
    puis les enregistre dans un fichier texte trié alphabétiquement.

    :param input_xml_file: Le chemin du fichier xml contenant les articles.
    :param output_file: Le chemin du fichier texte où les mots extraits seront sauvegardés.
    :return: None
    """
    tree = etree.parse(input_xml_file)

    with open(output_file, "w", encoding="utf-8") as file:
        # Initialisation d'un dataframe vide pour stocker les mots extraits
        df_words_sorted = pd.DataFrame(columns=["word"])

        for article in tree.xpath("/corpus/article"):
            # On tokenise le titre et le texte de l'article
            titre = tokenize(article.find("titre").text)
            texte = tokenize(article.find("texte").text)

            liste = titre + texte

            # Création d'un dataframe temporaire pour ajouter ces mots à la liste principale
            df_liste = pd.DataFrame(liste, columns=["word"])
            df_words_sorted = pd.concat([df_words_sorted, df_liste], ignore_index=True)

        # Suppression des doublons et trie des mots par ordre alphabétique
        df_words_sorted = df_words_sorted.drop_duplicates()
        df_words_sorted.sort_values(by="word", inplace=True)

        # Écriture dans le fichier de sortie
        df_words_sorted.to_csv(file, index=False, header=False)
        file.write("\n")


def create_lemma_spacy(input_file: str, output_file: str) -> None:
    """
    Crée des lemmes à partir des mots d'un fichier en utilisant spaCy,
    puis les enregistre dans un fichier de sortie.

    :param input_file: Le chemin du fichier contenant les mots à traiter.
    :param output_file: Le chemin du fichier où les lemmes seront sauvegardés.
    :return: None
    """
    # Modèle de langue français de spaCy
    nlp = spacy.load("fr_core_news_sm")

    with open(input_file, "r", encoding="utf-8") as words_file:
        words = words_file.read()

        # Extraction de tous les mots à l'aide d'une regex
        words = re.findall(r"\b\w+\b", words)

        # Transformation en une seule chaîne de caractères pour spaCy
        words = " ".join(words)

        # Traitement du texte avec spaCy pour obtenir des objets doc contenant les lemmes
        words = nlp(words)

        # Ouverture du fichier de sortie pour y écrire les lemmes
        with open(output_file, "w", encoding="utf-8") as file:
            for doc in words:
                file.write(f"{doc.text} → {doc.lemma_}\n")


def create_lemma_stemmer(input_file: str, output_file: str) -> None:
    """
    Crée des lemmes à partir des mots d'un fichier en utilisant le stemming,
    puis les enregistre dans un fichier de sortie.

    :param input_file: Le chemin du fichier contenant les mots à traiter.
    :param output_file: Le chemin du fichier où les lemmes seront sauvegardés.
    :return: None
    """
    with open(input_file, "r", encoding="utf-8") as words_file:
        words = words_file.read()

        # Extraction de tous les mots à l'aide d'une regex
        words = re.findall(r"\b\w+\b", words)

        # Initialisation du stemmer pour la langue française
        stemmer = FrenchStemmer()

        # Ouverture du fichier de sortie pour y écrire les lemmes
        with open(output_file, "w", encoding="utf-8") as file:
            for word in words:
                file.write(f"{word} → {stemmer.stem(word)} \n")


def compute_stats_lemma(algo: str, input_file: str) -> None:
    """
    Calcule le nombre de lemmes uniques et le taux de compression lexicale

    :param algo: Le nom de l'algorithme utilisé ('spacy' ou 'stemmer').
    :param input_file: Le fichier contenant les mots segmentés.
    :return: None
    """
    if algo == "spacy":
        create_lemma_spacy(input_file, "lemma_spacy.txt")
        lemma_dataframe = pd.read_csv(
            "lemma_spacy.txt", sep="→", header=None, names=["word", "lemma"]
        )
    elif algo == "stemmer":
        create_lemma_stemmer(input_file, "lemma_stemmer.txt")
        lemma_dataframe = pd.read_csv(
            "lemma_stemmer.txt", sep="→", header=None, names=["word", "lemma"]
        )

    # Calcul du nombre de lemmes uniques et du taux de compression lexicale
    unique_lemma = lemma_dataframe.nunique(axis=0).iloc[1]
    words = lemma_dataframe.nunique(axis=0).iloc[0]
    taux_compression_lexicale = (unique_lemma / words) * 100
    taux_compression_lexicale = round(taux_compression_lexicale, 2)
    print(
        f"Avec l'algorithme {algo}, nous avons {unique_lemma} lemmes uniques sur {words} mots "
        f"(un taux de compression lexicale de {taux_compression_lexicale}%)."
    )


def complete_subs_file(lemma_file: str, subs_file: str) -> None:
    """
    Ajoute les substitutions (termes -> lemme) à un fichier représentant
    un anti-dictionnaire.

    :param lemma_file: Le nom du fichier contenant les lemmes.
    :param subs_file: Le fichier contenant l'anti-dictionnaire.
    :return: None
    """
    # Ouverture du fichier des substitutions en mode append
    # (les termes de l'anti dictionnaire sont deja présents)
    with open(subs_file, "a", encoding="utf-8") as subs:
        with open(lemma_file, "r", encoding="utf-8") as lemma:
            for line in lemma:
                # Extraction du mot d'origine et de sa substitution
                word = line.split("→")[0].strip()
                substitute = line.split("→")[1].strip()
                subs.write(f"{word}\t{substitute}\n")


if __name__ == "__main__":
    extract_words_from_xml("../corpus_clean.xml", "../words_segmentation_clean.txt")
    create_lemma_spacy("../words_segmentation_clean.txt", "../lemma_spacy.txt")
    create_lemma_stemmer("../words_segmentation_clean.txt", "../lemma_stemmer.txt")
    compute_stats_lemma("spacy", "../words_segmentation_clean.txt")
    compute_stats_lemma("stemmer", "../words_segmentation_clean.txt")
    complete_subs_file("../lemma_stemmer.txt", "../subs.txt")
    create_clean_xml_corpus("../corpus.xml", "../subs.txt", "../corpus_clean.xml")
