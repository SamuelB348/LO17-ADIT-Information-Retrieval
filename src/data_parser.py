"""
Toutes les fonctions qui permettent de parser un corpus de documents
et de retourner le contenu sous format XML.
"""

from __future__ import annotations
import os
import pprint
import re
from typing import Optional, List, Tuple
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element
from xml.dom import minidom
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm
from utils import open_file, unzip_data


def extract_file_name(soup_content: BeautifulSoup) -> Optional[str]:
    """
    Extrait le nom du fichier à partir du contenu HTML.

    :param soup_content: L'objet Beautifulsoup représentant le contenu HTML.
    :return: Le nom du fichier ou None si non trouvé.
    """
    if not isinstance(soup_content, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    a_tags: List[Tag] = [
        a
        for a in soup_content.find_all("a", attrs={"data-url": True})
        if isinstance(a, Tag)
    ]
    for a in a_tags:
        # Extraire le nom du fichier sans son extension
        # Le nom est après le dernier "/" et avant le ".htm"
        file_name = str(a["data-url"]).rsplit("/", maxsplit=1)[-1].split(".")[0]

        if file_name.isdigit():  # Vérification qu'il s'agit d'un numéro
            return file_name
    return None


def extract_bulletin_number(soup_content: BeautifulSoup) -> Optional[str]:
    """
    Extrait le numéro du bulletin à partir du contenu HTML.

    :param soup_content: L'objet BeautifulSoup représentant le contenu HTML.
    :return: Le numéro du bulletin ou None si non trouvé.
    """
    if not isinstance(soup_content, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    full_title = soup_content.find("title")
    if full_title:
        title_text = full_title.get_text(strip=True)
        if ">" in title_text:
            # Récupération du texte après le premier '>' dans la balise <title>
            full_bulletin_number = title_text.split(">")[1]
            # Extraction du dernier élément (numéro seulement)
            bulletin_number = full_bulletin_number.split()[-1].strip()

            if bulletin_number.isdigit():  # Vérification qu'il s'agit d'un numéro
                return bulletin_number
    return None


def extract_date(soup_content: BeautifulSoup) -> Optional[str]:
    """
    Extrait la date de l'article à partir du contenu HTML.

    :param soup_content: L'objet BeautifulSoup représentant le contenu HTML.
    :return: La date de l'article ou None si non trouvée.
    """
    if not isinstance(soup_content, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    full_title = soup_content.find("title")
    if full_title:
        # Récupération du texte avant ">" dans la balise <title>
        title_text = full_title.get_text(strip=True)
        if ">" in title_text:
            date_str = title_text.split(">")[0].strip()
            try:
                # Date sous le format attendu
                formatted_date = datetime.strptime(date_str, "%Y/%m/%d").strftime(
                    "%d/%m/%Y"
                )
                return formatted_date
            except ValueError:
                return None
    return None


def extract_section(soup_content: BeautifulSoup) -> Optional[str]:
    """
    Extrait la rubrique de l'article à partir du contenu HTML.

    :param soup_content: L'objet BeautifulSoup représentant le contenu HTML.
    :return: La rubrique de l'article ou None si non trouvée.
    """
    if not isinstance(soup_content, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    span42_tags: List[Tag] = [
        tag
        for tag in soup_content.find_all("span", {"class": "style42"})
        if isinstance(tag, Tag)
    ]

    # Vérification que la liste contient au moins 2 éléments pour accéder au deuxième
    if len(span42_tags) > 1:
        # Récupération du deuxième élément de la liste et extraction du contenu
        # .replace() car fichier 70425 a "Actualité-Innovation" (avec un tiret)
        rubrique = str(span42_tags[1].contents[0]).strip().replace("-", " ")
        if all(
            (c.isalpha() or c.isspace()) for c in rubrique
        ):  # Vérification que tous les caractères sont alphabétiques ou des espaces
            return rubrique
    return None


def extract_title(soup_content: BeautifulSoup) -> Optional[str]:
    """
    Extrait le titre de l'article à partir du contenu HTML.

    :param soup_content: L'objet BeautifulSoup représentant le contenu HTML.
    :return: Le titre de l'article ou None si non trouvé.
    """
    if not isinstance(soup_content, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    full_title = soup_content.find("title")
    if full_title:
        # Récupération de la troisième partie après le deuxième ">" dans la balise <title>
        return full_title.text.split(">")[2].strip()
    return None


def extract_author(soup_content: BeautifulSoup) -> Optional[str]:
    """
    Extrait le nom du rédacteur à partir du contenu HTML.

    :param soup_content: L'objet BeautifulSoup représentant le contenu HTML.
    :return: Le nom du rédacteur ou None si non trouvé.
    """
    if not isinstance(soup_content, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    tr_parent = None
    # Recherche du tableau <tr> contenant le nom du rédacteur
    tr_tags: List[Tag] = [
        tag for tag in soup_content.find_all("tr") if isinstance(tag, Tag)
    ]
    for tr in tr_tags:
        span = tr.find("span", {"class": "style28"})
        if span and (
            span.get_text().strip() == "Rédacteurs :"
            or span.get_text().strip() == "Rédacteur :"
        ):
            tr_parent = tr
            break

    if tr_parent:
        # Recherche du <span> avec la classe 'style95' dans le <tr> parent
        span_95 = tr_parent.find("span", {"class": "style95"})
        if span_95:
            # Extraction du texte du rédacteur
            author_text = span_95.get_text(strip=True)
            match = re.search(
                r"ADIT\s*-\s*([A-Za-zÀ-ÿ0-9]+(?:[-'\s][A-Za-zÀ-ÿ0-9]+)*)\s*-.*",
                author_text,
            )
            if match:
                return match.group(1).strip()  # Retourne le nom du rédacteur
    return None


def extract_text(soup_content: BeautifulSoup) -> Optional[str]:
    """
    Extrait le texte à partir du contenu HTML.

    :param soup_content: L'objet beautifulsoup représentant le contenu HTML.
    :return: Une liste contenant le texte extrait ou none si non trouvé.
    """
    if not isinstance(soup_content, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    parent: List[Tag] = [
        tag
        for tag in soup_content.find_all(
            "td", {"class": "FWExtra2", "bgcolor": "#f3f5f8"}
        )
        if isinstance(tag, Tag)
    ]
    text = parent[0].find_all("span", {"class": "style95"})
    content = ""
    if text:
        for txt in text:
            cleaned_text = txt.get_text().replace("\n", "")
            content += " " + cleaned_text
        return content.strip()
    return None


def extract_images(soup_content: BeautifulSoup) -> List[Tuple[str, str]]:
    """
    Extrait les images (sources et légendes) à partir du contenu HTML.

    :param soup_content: L'objet BeautifulSoup représentant le contenu HTML.
    :return: Une liste contenant les tuples (lien, légende) des images.
    """

    if not isinstance(soup_content, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    images = []
    parents: List[Tag] = [
        tag
        for tag in soup_content.find_all(
            "td", {"class": "FWExtra2", "bgcolor": "#f3f5f8"}
        )
        if isinstance(tag, Tag)
    ]
    divs: List[Tag] = [
        tag for tag in parents[0].find_all("div") if isinstance(tag, Tag)
    ]
    for div in divs:
        img = div.find("img")
        if img and isinstance(img, Tag):
            img_src = str(img.get("src"))
            caption = ""
            span = div.find("span", {"class": "style21"})
            if span:
                caption = span.get_text(strip=True)
            images.append((img_src, caption))

    return images


def extract_contacts(soup_content: BeautifulSoup) -> Optional[str]:
    """
    Extrait les contacts à partir du contenu HTML.

    :param soup_content: L'objet BeautifulSoup représentant le contenu HTML.
    :return: Une liste de contacts extraits ou une liste vide si aucun contact n'est trouvé.
    """
    if not isinstance(soup_content, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    td_parent = None
    # On récupère le <td> qui précède celui qu'on cherche
    spans: List[Tag] = [
        tag
        for tag in soup_content.find_all("span", {"class": "style28"})
        if isinstance(tag, Tag)
    ]
    for span in spans:
        if span.get_text(strip=True) == "Pour en savoir plus, contacts :":
            td_parent = span.find_parent("td")
            break

    if td_parent:
        target_td = td_parent.find_next_sibling("td")
        if target_td and isinstance(target_td, Tag):
            span_85 = target_td.find("span", {"class": "style85"})
            if span_85:
                return span_85.get_text(strip=True)

    return None


def check_all(verbose=False) -> bool:
    """
    Fonction pour vérifier toutes les étapes de l'extraction.
    :param verbose: Affiche tout le contenu extrait si mis à True.
    :return: Un booléen indiquant si tout s'est bien passé.
    """
    is_ok = True
    folder = unzip_data("../BULLETINS.zip", "data")
    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ]

    for file_path in tqdm(files, desc="Vérification des n° de fichier"):
        soup = open_file(file_path)
        file_name = extract_file_name(soup)
        if not file_name:
            print(
                f"Erreur: {os.path.basename(file_path)} ne contient pas de nom valide."
            )
            is_ok = False
        elif verbose:
            print(file_name)

    for file_path in tqdm(files, desc="Vérification des n° de bulletin"):
        soup = open_file(file_path)
        bulletin_number = extract_bulletin_number(soup)
        if not bulletin_number:
            print(
                f"Erreur: {os.path.basename(file_path)} ne contient pas "
                f"de n° de bulletin valide."
            )
            is_ok = False
        elif verbose:
            print(bulletin_number)

    for file_path in tqdm(files, desc="Vérification des dates"):
        soup = open_file(file_path)
        date = extract_date(soup)
        if not date:
            print(
                f"Erreur: {os.path.basename(file_path)} ne contient pas de date valide."
            )
            is_ok = False
        elif verbose:
            print(date)

    for file_path in tqdm(files, desc="Vérification des rubriques"):
        soup = open_file(file_path)
        rubrique = extract_section(soup)
        if not rubrique:
            print(
                f"Erreur: {os.path.basename(file_path)} ne contient pas de rubrique valide."
            )
            is_ok = False
        elif verbose:
            print(rubrique)

    for file_path in tqdm(files, desc="Vérification des titres"):
        soup = open_file(file_path)
        title = extract_title(soup)
        if not title:
            print(f"Erreur: {os.path.basename(file_path)} ne contient pas de titre.")
            is_ok = False
        elif verbose:
            print(title)

    for file_path in tqdm(files, desc="Vérification des auteurs"):
        soup = open_file(file_path)
        author = extract_author(soup)
        if not author:
            print(
                f"Erreur: {os.path.basename(file_path)} ne contient "
                f"pas de nom de rédacteur valide."
            )
            is_ok = False
        elif verbose:
            print(author)

    for file_path in tqdm(files, desc="Vérification des contenus"):
        soup = open_file(file_path)
        text = extract_text(soup)
        if not text:
            print(
                f"Erreur: {os.path.basename(file_path)} ne contient pas de texte valide."
            )
            is_ok = False
        elif verbose:
            print(text)

    for file_path in tqdm(files, desc="Vérification des images"):
        soup = open_file(file_path)
        images = extract_images(soup)
        if verbose:
            pprint.pprint(images)

    for file_path in tqdm(files, desc="Vérification des contacts"):
        soup = open_file(file_path)
        contacts = extract_contacts(soup)
        if not contacts:
            print(f"Erreur: {os.path.basename(file_path)} ne contient pas de contact.")
            is_ok = False
        elif verbose:
            print(contacts)

    return is_ok


def generate_article(file_name: str) -> Optional[Element]:
    """
    Génère un article au format XML

    :param file_name: Le fichier HTML à traiter.
    :return: Une chaîne XML représentant l'article.
    """
    try:
        soup = open_file(file_name)

        # Création de l'élément XML principal
        article = ET.Element("article")

        # Ajout des sous-éléments à l'article en utilisant les fonctions d'extraction
        ET.SubElement(article, "fichier").text = extract_file_name(soup)
        ET.SubElement(article, "numero").text = extract_bulletin_number(soup)
        ET.SubElement(article, "date").text = extract_date(soup)
        ET.SubElement(article, "rubrique").text = extract_section(soup)
        ET.SubElement(article, "titre").text = extract_title(soup)
        ET.SubElement(article, "auteur").text = extract_author(soup)
        ET.SubElement(article, "texte").text = extract_text(soup)

        images = extract_images(soup)
        images_elem = ET.SubElement(article, "images")
        # 'images' est une liste dont chaque élément devient une image
        for url, caption in images:
            image_elem = ET.SubElement(images_elem, "image")
            ET.SubElement(image_elem, "urlImage").text = url.strip()
            ET.SubElement(image_elem, "legendeImage").text = caption.strip()

        ET.SubElement(article, "contact").text = extract_contacts(soup)

        return article

    except Exception as e:
        print(f"Erreur lors de la génération de l'article avec {file_name} : {e}")
        return None


def generate_corpus(zip_directory: str, output_file: str) -> None:
    """
    Génère un corpus au format XML et l'enregistre dans un fichier.

    :param zip_directory: Le répertoire contenant le fichier ZIP à traiter.
    :param output_file: Le fichier où le corpus XML sera sauvegardé.
    :return: None.
    """
    try:
        workdir = unzip_data(zip_directory, "/..")
        corpus = ET.Element("corpus")

        for element in tqdm(os.listdir(workdir), desc="Genération du corpus"):
            file_path = os.path.join(workdir, element)
            if os.path.isfile(file_path):
                article = generate_article(file_path)
                if article is not None:
                    corpus.append(article)
                else:
                    raise ValueError(
                        f"Impossible de générer l'article pour {file_path}"
                    )

        # Utilisation de minidom pour avoir des indentations
        xml_str = minidom.parseString(ET.tostring(corpus)).toprettyxml(indent="  ")

        # Sauvegarde du contenu dans un fichier
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(xml_str)
            print(f"Corpus généré avec succès dans: {output_file}")

    except FileNotFoundError as fnf_error:
        print(
            f"Erreur: fichier ou répertoire spécifié non trouvé. Détails: {fnf_error}"
        )
    except Exception as e:
        print(f"Erreur: lors de la génération du corpus: {e}")


if __name__ == "__main__":
    if check_all():
        generate_corpus("../BULLETINS.zip", "data/corpus.xml")
    else:
        print("Problème durant la vérification des fichiers !")
