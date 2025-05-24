"""
Fonctions pour créer un index inversé du corpus lemmatisé.
"""

import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import List
from utils import parse_xml


def creation_index_inverse(
    root: ET.Element, tags: List[str]
) -> dict[str, dict[str, dict[str, int]]]:
    """
    Crée un index inversé sous forme de dictionnaire à partir d'un corpus XML.

    :param root: Élément racine du fichier XML.
    :param tags: Liste des balises à indexer.
    :return: Dictionnaire ayant la structure lemme → {doc_id → {tag → fréquence}}.
    """

    index_inverse: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )

    for article in root.findall("article"):
        doc_id = article.findtext("fichier", default="inconnu")

        for tag in tags:
            element = article.find(tag)
            texte = element.text if element is not None else None

            # Cas spécial : images
            if tag == "images":
                if texte:
                    index_inverse["presence_image"][doc_id][tag] += 1
                else:
                    index_inverse["pas_image"][doc_id][tag] += 1
                continue

            # Cas spécial : rubrique
            if tag == "rubrique":
                if texte:
                    mot = texte.strip().lower()
                    index_inverse[mot][doc_id][tag] += 1
                continue

            if not texte:
                continue

            # Cas général
            mots = texte.lower().split()
            for mot in mots:
                mot = mot.strip()
                if mot:
                    index_inverse[mot][doc_id][tag] += 1

    return index_inverse


def sauvegarde_index_inverse(
    index_inverse: dict[str, dict[str, dict[str, int]]], fichier_sortie: str
):
    """
    Sauvegarde un index inverse dans un fichier texte trié alphabétiquement

    :param index_inverse: Dictionnaire contenant l'index inverse
    :param fichier_sortie: Chemin du fichier texte de sortie
    :return: None
    """
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        # Parcours des mots triés alphabétiquement
        for mot in sorted(index_inverse.keys()):
            liste_docs = []
            for doc_id, tags in index_inverse[mot].items():
                for tag, _ in tags.items():
                    liste_docs.append(f"{doc_id}:{tag}")
            f.write(f"{mot},{','.join(liste_docs)}\n")


if __name__ == "__main__":
    tags_a_indexer = [
        "fichier",
        "numero",
        "date",
        "rubrique",
        "titre",
        "texte",
        "images",
    ]
    FICHIER_XML = "data/corpus_clean.xml"
    print("Création de l'index inversé...")
    index = creation_index_inverse(parse_xml(FICHIER_XML), tags_a_indexer)
    print("Sauvegarde de l'index inversé...")
    sauvegarde_index_inverse(index, "data/index_inverse.txt")
