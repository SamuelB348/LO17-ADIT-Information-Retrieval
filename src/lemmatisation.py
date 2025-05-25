"""
Fonctions pour lemmatiser le corpus selon différentes approches.
"""

import spacy
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib_venn import venn2
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


def lemmatisation_spacy(fichier_entree: str, fichier_sortie: str) -> None:
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


def lemmatisation_stemmer(fichier_entree: str, fichier_sortie: str) -> None:
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


def calcul_stats_lemmes(fichier_spacy: str, fichier_stemmer: str) -> None:
    """
    Calcule le nombre de lemmes uniques et le taux de compression lexicale
    et donne des représentations graphiques.

    :param fichier_spacy: Le fichier des lemmes Spacy.
    :param fichier_stemmer: Le fichier des lemmes stemmer.
    :return: None
    """
    spacy_df = pd.read_csv(
        fichier_spacy,
        sep="→",
        header=None,
        names=["word", "lemma"],
        engine="python",
    )
    stemmer_df = pd.read_csv(
        fichier_stemmer,
        sep="→",
        header=None,
        names=["word", "lemma"],
        engine="python",
    )

    ###########################################
    # Quelques stats générales
    ###########################################

    # Fonction pour calculer et afficher le taux de compression lexicale
    def compression_lexicale(dataframe, nom_methode):
        mots_uniques = dataframe.nunique().iloc[0]
        lemmes_uniques = dataframe.nunique().iloc[1]
        taux = round((lemmes_uniques / mots_uniques) * 100, 2)
        print(
            f"Avec {nom_methode}, {lemmes_uniques} lemmes uniques sur {mots_uniques} mots "
            f"(taux de compression lexicale : {taux}%)."
        )

    # Fonction pour calculer les 20 lemmes les plus présents
    def plot_lemma_distribution(df_spacy, df_stemmer):
        top_spacy = df_spacy["lemma"].value_counts().head(20)
        top_stemmer = df_stemmer["lemma"].value_counts().head(20)

        plt.figure(figsize=(14, 5))

        plt.subplot(1, 2, 1)
        top_spacy.plot(kind="bar")
        plt.title("Top 20 lemmes (SpaCy)")
        plt.xticks(rotation=45)

        plt.subplot(1, 2, 2)
        top_stemmer.plot(kind="bar", color="orange")
        plt.title("Top 20 lemmes (Snowball Stemmer)")
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    compression_lexicale(spacy_df, "Spacy")
    compression_lexicale(stemmer_df, "Stemmer")
    plot_lemma_distribution(spacy_df, stemmer_df)

    lemmes_uniques_spacy = set(spacy_df["lemma"].astype(str).str.strip().str.lower())
    lemmes_uniques_stemmer = set(
        stemmer_df["lemma"].astype(str).str.strip().str.lower()
    )

    plt.figure(figsize=(6, 6))
    venn2(
        (lemmes_uniques_spacy, lemmes_uniques_stemmer), set_labels=("SpaCy", "Stemmer")
    )
    plt.title("Diagramme de Venn des lemmes uniques")
    plt.show()

    ###########################################
    # Quelques stats sur un échantillon de mots
    ###########################################

    mots = [
        "électromagnétique",
        "atome",
        "moléculaire",
        "molécules",
        "réaction",
        "réactifs",
        "cellules",
        "cellulaire",
        "bactérie",
        "bactérienne",
        "électrons",
        "électronique",
        "photosynthèse",
        "équation",
        "équations",
        "intégrale",
        "intégration",
        "différentielle",
        "différentiels",
        "gènes",
        "génomique",
        "mutation",
        "mutagène",
        "neurones",
        "neuronale",
        "synapse",
    ]

    nlp = spacy.load("fr_core_news_sm")
    doc = nlp(" ".join(mots))
    lemmes_spacy = [token.lemma_ for token in doc]

    stemmer = FrenchStemmer()
    stems_snowball = [stemmer.stem(mot) for mot in mots]

    # Tableau comparatif
    df = pd.DataFrame(
        {
            "mot_original": mots,
            "lemmatisation_spacy": lemmes_spacy,
            "stem_snowball": stems_snowball,
        }
    )

    nb_lemmes = len(set(lemmes_spacy))
    nb_stems = len(set(stems_snowball))

    print(df)
    print("\nNombre de lemmes uniques (SpaCy) :", nb_lemmes)
    print("Nombre de stems uniques (Snowball) :", nb_stems)

    # Nombre de lemmes identiques au mot de base
    nb_lemmes_identiques = sum(
        1 for mot, lemme in zip(mots, lemmes_spacy) if mot == lemme
    )
    nb_stems_identiques = sum(
        1 for mot, stem in zip(mots, stems_snowball) if mot == stem
    )
    print("\nNombre de lemmes identiques au terme (SpaCy) :", nb_lemmes_identiques)
    print("Nombre de stems identiques au terme (Snowball) :", nb_stems_identiques)

    # Longueur des lemmes
    long_spacy = [len(lemme) for lemme in lemmes_spacy]
    long_stem = [len(stem) for stem in stems_snowball]

    plt.figure(figsize=(6, 5))
    plt.boxplot([long_spacy, long_stem], labels=["SpaCy", "Stemmer"])
    plt.title("Boxplot des longueurs de lemmes")
    plt.ylabel("Longueur des lemmes")
    plt.grid(True)
    plt.show()


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
    lemmatisation_spacy("data/words_segmentation_clean.txt", "data/lemma_spacy.txt")
    print("Lemmatisation avec SnowBall...")
    lemmatisation_stemmer("data/words_segmentation_clean.txt", "data/lemma_stemmer.txt")
    print("Calcul de statistiques...")
    calcul_stats_lemmes("data/lemma_spacy.txt", "data/lemma_stemmer.txt")
    print("Mis-à-jour du fichier de substitution...")
    ajout_fichier_subs("data/lemma_stemmer.txt", "data/subs.txt")
    print("Nettoyage du corpus...")
    nettoyage_corpus_xml("data/corpus.xml", "data/subs.txt", "data/corpus_clean.xml")
