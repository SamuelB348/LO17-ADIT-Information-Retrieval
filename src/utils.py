"""
Fonctions utilitaires
"""

import os
import zipfile
import re
from typing import List
from bs4 import BeautifulSoup


def unzip_data(zip_name: str, output_dir: str) -> str:
    """
    Extrait le contenu d'un fichier zip dans un répertoire.

    :param zip_name: Le nom du fichier zip à décompresser.
    :param output_dir : Le nom du répertoire de destination.
    :return: None.
    """
    # TODO : ajouter vérification sur la nature du zip
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
    return re.findall(r"\b\w+\b", text.lower())
