"""
Fonctions pour lemmatiser le corpus selon différentes approches.
"""

import spacy
import pandas as pd
from nltk.stem.snowball import FrenchStemmer
from lxml import etree
from anti_dictionnaire import nettoyage_corpus_xml
from utils import tokenize


def extract_mots_xml(fichier_xml: str, fichier_sortie: str) -> None:
    """
    Extrait les mots des balises <titre> et <texte> d'un fichier xml, les normalise simplement,
    puis les enregistre dans un fichier texte trié alphabétiquement.

    :param fichier_xml: Le chemin du fichier xml contenant les articles.
    :param fichier_sortie: Le chemin du fichier texte où les mots extraits seront sauvegardés.
    :return: None
    """
    tree = etree.parse(fichier_xml)

    # Initialisation d'un dataframe vide pour stocker les mots extraits
    df_mots_tries = pd.DataFrame(columns=["word"])

    for article in tree.xpath("/corpus/article"):
        # On tokenise le titre et le texte de l'article
        titre = tokenize(article.find("titre").text)
        texte = tokenize(article.find("texte").text)

        liste = titre + texte

        # Création d'un dataframe temporaire pour ajouter ces mots à la liste principale
        df_liste = pd.DataFrame(liste, columns=["word"])
        df_mots_tries = pd.concat([df_mots_tries, df_liste], ignore_index=True)

    # Suppression des doublons et trie des mots par ordre alphabétique
    df_mots_tries = df_mots_tries.drop_duplicates()
    df_mots_tries.sort_values(by="word", inplace=True)

    # Écriture dans le fichier de sortie
    df_mots_tries.to_csv(fichier_sortie, index=False, header=False)


def lemmes_spacy(fichier_entree: str, fichier_sortie: str) -> None:
    """
    Crée des lemmes à partir des mots d'un fichier en utilisant spaCy,
    puis les enregistre dans un fichier de sortie.

    :param fichier_entree: Le chemin du fichier contenant les mots à traiter.
    :param fichier_sortie: Le chemin du fichier où les lemmes seront sauvegardés.
    :return: None
    """
    # Modèle de langue français de spaCy
    nlp = spacy.load("fr_core_news_sm")

    with open(fichier_entree, "r", encoding="utf-8") as fichier_mots:
        # Extraction de tous les mots sous forme de liste
        mots_liste = [ligne.strip() for ligne in fichier_mots if ligne.strip()]

    # Transformation en une seule chaîne de caractères pour spaCy
    mots_str = " ".join(mots_liste)

    # Traitement du texte avec spaCy pour obtenir des objets doc contenant les lemmes
    mots_spacy = nlp(mots_str)

    # Ouverture du fichier de sortie pour y écrire les lemmes
    with open(fichier_sortie, "w", encoding="utf-8") as file:
        for doc in mots_spacy:
            file.write(f"{doc.text}→{doc.lemma_}\n")


def lemmes_stemmer(fichier_entree: str, fichier_sortie: str) -> None:
    """
    Crée des lemmes à partir des mots d'un fichier en utilisant le stemming,
    puis les enregistre dans un fichier de sortie.

    :param fichier_entree: Le chemin du fichier contenant les mots à traiter.
    :param fichier_sortie: Le chemin du fichier où les lemmes seront sauvegardés.
    :return: None
    """
    with open(fichier_entree, "r", encoding="utf-8") as fichier_mots:
        # Extraction de tous les mots sous forme de liste
        mots = [ligne.strip() for ligne in fichier_mots if ligne.strip()]

    # Initialisation du stemmer pour la langue française
    stemmer = FrenchStemmer()

    # Ouverture du fichier de sortie pour y écrire les lemmes
    with open(fichier_sortie, "w", encoding="utf-8") as file:
        for mot in mots:
            file.write(f"{mot}→{stemmer.stem(mot)}\n")


def calcul_stats_lemmes(algo: str, input_file: str) -> None:
    """
    Calcule le nombre de lemmes uniques et le taux de compression lexicale

    :param algo: Le nom de l'algorithme utilisé ('spacy' ou 'stemmer').
    :param input_file: Le fichier contenant les mots segmentés.
    :return: None
    """
    # TODO: compléter ça avec toutes les stats du colab
    if algo == "spacy":
        lemmes_spacy(input_file, "data/lemma_spacy.txt")
        lemma_dataframe = pd.read_csv(
            "data/lemma_spacy.txt",
            sep="→",
            header=None,
            names=["word", "lemma"],
            engine="python",
        )
    elif algo == "stemmer":
        lemmes_stemmer(input_file, "data/lemma_stemmer.txt")
        lemma_dataframe = pd.read_csv(
            "data/lemma_stemmer.txt",
            sep="→",
            header=None,
            names=["word", "lemma"],
            engine="python",
        )
    else:
        raise ValueError(f"Algorithme '{algo}' n'existe pas.")

    # Calcul du nombre de lemmes uniques et du taux de compression lexicale
    unique_lemma = lemma_dataframe.nunique(axis=0).iloc[1]
    words = lemma_dataframe.nunique(axis=0).iloc[0]
    taux_compression_lexicale = (unique_lemma / words) * 100
    taux_compression_lexicale = round(taux_compression_lexicale, 2)
    print(
        f"Avec l'algorithme {algo}, nous avons {unique_lemma} lemmes uniques sur {words} mots "
        f"(un taux de compression lexicale de {taux_compression_lexicale}%)."
    )


def ajout_fichier_subs(fichier_lemmes: str, fichier_subs: str) -> None:
    """
    Ajoute les substitutions (termes -> lemme) à un fichier représentant
    un anti-dictionnaire.

    :param fichier_lemmes: Le nom du fichier contenant les lemmes.
    :param fichier_subs: Le fichier contenant l'anti-dictionnaire.
    :return: None
    """
    # Ouverture du fichier des substitutions en mode append
    # (les termes de l'anti dictionnaire sont deja présents)
    with open(fichier_subs, "a", encoding="utf-8") as subs:
        with open(fichier_lemmes, "r", encoding="utf-8") as lemma:
            for ligne in lemma:
                # Extraction du mot d'origine et de sa substitution
                mot = ligne.split("→")[0].strip()
                substitut = ligne.split("→")[1].strip()
                subs.write(f"{mot}\t{substitut}\n")


if __name__ == "__main__":
    print("Nouvelle segmentation du corpus...")
    extract_mots_xml(
        "data/corpus_wo_stopwords.xml", "data/words_segmentation_clean.txt"
    )
    print("Lemmatisation avec Spacy...")
    lemmes_spacy("data/words_segmentation_clean.txt", "data/lemma_spacy.txt")
    print("Lemmatisation avec SnowBall...")
    lemmes_stemmer("data/words_segmentation_clean.txt", "data/lemma_stemmer.txt")
    print("Calcul de statistiques...")
    calcul_stats_lemmes("spacy", "data/words_segmentation_clean.txt")
    calcul_stats_lemmes("stemmer", "data/words_segmentation_clean.txt")
    print("Mis-à-jour du fichier de substitution...")
    ajout_fichier_subs("data/lemma_stemmer.txt", "data/subs.txt")
    print("Nettoyage du corpus...")
    nettoyage_corpus_xml("data/corpus.xml", "data/subs.txt", "data/corpus_clean.xml")
