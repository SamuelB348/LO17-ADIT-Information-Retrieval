"""
Fichier permettant de découper le corpus (les titres et les textes) en tokens.
"""

from lxml import etree
from utils import tokenize


def segmente_corpus(input_corpus: str, output_file: str) -> None:
    """
    Segmente un corpus XML en associant les tokens avec le nom de fichier.

    :param input_corpus: Le chemin du fichier XML à traiter.
    :param output_file: Le chemin du fichier de sortie où seront écrites
     les paires token-numéro de fichier (lié à l'article).
    :return: None
    """
    tree = etree.parse(input_corpus)

    with open(output_file, "w", encoding="utf-8") as file:
        for article in tree.xpath("/corpus/article"):
            titre = tokenize(article.find("titre").text)
            texte = tokenize(article.find("texte").text)
            liste = titre + texte  # Combine les tokens du titre et du texte

            # Écriture des tokens avec le numéro de l'article dans le fichier
            for token in liste:
                file.write(f"{token}\t{article.find('fichier').text}\n")


if __name__ == "__main__":
    segmente_corpus("../corpus.xml", "../words_segmentation.txt")
