"""
Fonctions utilitaires
"""

import os
import zipfile
import re
from typing import List
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup


def unzip_data(zip_name: str, output_dir: str) -> str:
    """
    Extrait le contenu d'un fichier zip dans un répertoire.

    :param zip_name: Le nom du fichier zip à décompresser.
    :param output_dir : Le nom du répertoire de destination.
    :return: None.
    """
    os.makedirs(output_dir, exist_ok=True)

    with zipfile.ZipFile(zip_name, "r") as zip_ref:
        zip_ref.extractall(output_dir)

    return os.path.join(output_dir, os.path.basename(zip_name).split(".zip")[0])


def open_file(file_name: str) -> BeautifulSoup:
    """
    Ouvre un fichier html et le charge avec beautifulsoup pour l'analyse.

    :param file_name: Le chemin du fichier html à ouvrir.
    :return: Un objet beautifulsoup représentant le contenu du fichier.
    """
    with open(file_name, "r", encoding="utf-8") as html_doc:
        return BeautifulSoup(html_doc, "html.parser")


def tokenize(text: str) -> List[str]:
    """
    Renvoie la liste des mots séparés par des délimiteurs non alphabétiques
    et convertis en minuscules.

    :param text: Le texte à tokeniser.
    :return: La liste des tokens extraits du texte.
    """
    return re.findall(r"\b\w+(?:-\w+)*\b", text.lower())


def parse_xml(file_path: str) -> ET.Element:
    """
    charge et parse un fichier xml

    :param file_path: chemin du fichier xml
    :return: élément racine de l'arbre xml
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root
