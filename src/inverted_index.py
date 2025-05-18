"""
Fonctions pour créer un index inversé du corpus lemmatisé.
"""

import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import List, Dict
from utils import parse_xml


def create_inverted_index(
    root: ET.Element, tags: List[str]
) -> Dict[str, Dict[str, Dict[str, int]]]:
    """
    Crée un index inversé sous forme de dictionnaire à partir d'un corpus XML.

    :param root: Élément racine du fichier XML.
    :param tags: Liste des balises à indexer.
    :return: Dictionnaire ayant la structure lemme → {doc_id → {tag → fréquence}}.
    """

    inverted_index = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for article in root.findall("article"):
        doc_id = article.findtext("fichier", default="inconnu")

        for tag in tags:
            element = article.find(tag)
            text = element.text if element is not None else None

            # Cas spécial : images
            if tag == "images":
                if text:
                    inverted_index["presence_image"][doc_id][tag] += 1
                continue

            # Cas spécial : rubrique
            if tag == "rubrique":
                if text:
                    word = text.strip().lower()
                    inverted_index[word][doc_id][tag] += 1
                continue

            if not text:
                continue

            # Cas général
            words = text.lower().split()
            for word in words:
                word = word.strip()
                if word:
                    inverted_index[word][doc_id][tag] += 1

    return inverted_index


def save_inverted_index_txt(
    inverted_index: Dict[str, Dict[str, Dict[str, int]]], output_file: str
):
    """
    Sauvegarde un index inverse dans un fichier texte trié alphabétiquement

    :param inverted_index: Dictionnaire contenant l'index inverse
    :param output_file: Chemin du fichier texte de sortie
    :return: None
    """
    with open(output_file, "w", encoding="utf-8") as f:
        # Parcours des mots triés alphabétiquement
        for word in sorted(inverted_index.keys()):
            doc_list = []
            for doc_id, tags in inverted_index[word].items():
                for tag, _ in tags.items():
                    doc_list.append(f"{doc_id}:{tag}")
            f.write(f"{word},{', '.join(doc_list)}\n")


if __name__ == "__main__":
    tags_to_index = [
        "fichier",
        "numero",
        "date",
        "rubrique",
        "titre",
        "texte",
        "images",
    ]
    XML_FILE = "../corpus_clean.xml"
    index = create_inverted_index(parse_xml(XML_FILE), tags_to_index)
    save_inverted_index_txt(index, "../index_inverse.txt")
