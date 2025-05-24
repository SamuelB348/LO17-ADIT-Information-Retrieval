"""
Fichier permettant de découper le corpus (les titres et les textes) en tokens.
"""

from lxml import etree
from utils import tokenize


def segmente_corpus(corpus: str, fichier_sortie: str) -> None:
    """
    Segmente un corpus XML en associant les tokens avec le nom de fichier.

    :param corpus: Le chemin du fichier XML (corpus) à traiter.
    :param fichier_sortie: Le chemin du fichier de sortie où seront écrites
     les paires token-numéro de fichier (lié à l'article).
    :return: None
    """
    tree = etree.parse(corpus)

    with open(fichier_sortie, "w", encoding="utf-8") as file:
        for article in tree.xpath("/corpus/article"):
            titre = tokenize(article.find("titre").text)
            texte = tokenize(article.find("texte").text)
            liste = titre + texte  # Combine les tokens du titre et du texte

            # Écriture des tokens avec le numéro de l'article dans le fichier
            for token in liste:
                file.write(f"{token}\t{article.find('fichier').text}\n")


if __name__ == "__main__":
    print("Segmentation du corpus...")
    segmente_corpus("data/corpus.xml", "data/words_segmentation.txt")
