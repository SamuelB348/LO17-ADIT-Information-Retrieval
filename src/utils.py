"""
Fonctions utilitaires
"""

import os
import zipfile
import re
import calendar
from datetime import datetime
from typing import List, Tuple
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


def get_last_day_of_month(year: int, month: int) -> int:
    """
    Renvoie le dernier numéro de jour d'une mois, pour une année donnée.
    :param year: L'année.
    :param month: Le mois.
    :return: Un numéro.
    """
    _, last_day = calendar.monthrange(year, month)
    return last_day


def get_min_max_dates(date_str: str) -> Tuple[str, str]:
    """
    Renvoie un range de dates à partir d'un pattern de date.
    Ex : 2012-**-** → {2012-01-01, 2012-12-31}
    :param date_str: Une date sous forme de chaîne de caractères.
    :return: Un tuple (date minimale, date maximale)
    """
    # Nettoyage de la chaîne de caractères pour enlever les étoiles
    cleaned_date = date_str.replace("*", "")
    while cleaned_date.endswith("-"):
        cleaned_date = cleaned_date[:-1]

    print(cleaned_date)
    # Si la date est juste une année (comme "2012-**-**")
    if len(cleaned_date) == 4:  # Format "YYYY-**-**"
        min_date = f"{cleaned_date}-01-01"
        max_date = f"{cleaned_date}-12-31"
    elif len(cleaned_date) == 7:  # Format "YYYY-MM-**"
        annee, mois = cleaned_date.split("-")
        min_date = f"{annee}-{mois:02d}-01"
        max_day = get_last_day_of_month(int(annee), int(mois))
        max_date = f"{annee}-{mois:02d}-{max_day:02d}"
    elif len(cleaned_date) == 10:  # Format "YYYY-MM-DD"
        annee, mois, day = cleaned_date.split("-")
        min_date = f"{annee}-{mois}-{day}"
        max_date = f"{annee}-{mois}-{day}"
    else:
        raise ValueError(f"{date_str} format invalide")

    return min_date, max_date


def replace_min_and_max(date_dict):
    """
    Permet d'avoir des dates exactes dans un dictionnaire contenant des dates
    minimales et maximales sous forme de pattern.
    Ex : {'min' : 2012-**-**} → {'min' : 2012-01-01}
    :param date_dict: Le dictionnaire de dates.
    :return: Le dictionnaire modifié
    """
    if "min" in date_dict:
        date_dict["min"] = date_dict["min"].replace("*", "")
        while date_dict["min"].endswith("-"):
            date_dict["min"] = date_dict["min"][:-1]
        if len(date_dict["min"]) == 4:  # Format "YYYY-**-**"
            date_dict["min"] = f"{date_dict['min']}-01-01"

        elif len(date_dict["min"]) == 7:  # Format "YYYY-MM-**"
            year, month = date_dict["min"].split("-")
            year = int(year)
            month = int(month)
            date_dict["min"] = f"{year}-{month:02d}-01"
        elif len(date_dict["min"]) == 10:  # Format "YYYY-MM-DD"
            year, month, day = date_dict["min"].split("-")
            date_dict["min"] = f"{year}-{month}-{day}"
        # Retourner les dates sous le format jj/mm/yyyy
        date_dict["min"] = datetime.strptime(date_dict["min"], "%Y-%m-%d")
        date_dict["min"] = date_dict["min"].strftime("%d/%m/%Y")

    if "max" in date_dict:
        date_dict["max"] = date_dict["max"].replace("*", "")
        while date_dict["max"].endswith("-"):
            date_dict["max"] = date_dict["max"][:-1]
        if len(date_dict["max"]) == 4:  # Format "YYYY-**-**"
            date_dict["max"] = f"{date_dict['max']}-12-31"
        elif len(date_dict["max"]) == 7:  # Format "YYYY-MM-**"
            year, month = date_dict["max"].split("-")
            year = int(year)
            month = int(month)
            max_day = get_last_day_of_month(year, month)
            date_dict["max"] = f"{year}-{month:02d}-{max_day:02d}"
        elif len(date_dict["max"]) == 10:  # Format "YYYY-MM-DD"
            year, month, day = date_dict["max"].split("-")
            date_dict["max"] = f"{year}-{month}-{day}"
        # Retourner les dates sous le format jj/mm/yyyy
        date_dict["max"] = datetime.strptime(date_dict["max"], "%Y-%m-%d")
        date_dict["max"] = date_dict["max"].strftime("%d/%m/%Y")
