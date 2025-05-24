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


def extract_nom_fichier(contenu_soup: BeautifulSoup) -> Optional[str]:
    """
    Extrait le nom du fichier à partir du contenu HTML.

    :param contenu_soup: L'objet Beautifulsoup représentant le contenu HTML.
    :return: Le nom du fichier ou None si non trouvé.
    """
    if not isinstance(contenu_soup, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    a_tags: List[Tag] = [
        a
        for a in contenu_soup.find_all("a", attrs={"data-url": True})
        if isinstance(a, Tag)
    ]
    for a in a_tags:
        # Extraire le nom du fichier sans son extension
        # Le nom est après le dernier "/" et avant le ".htm"
        nom_fichier = str(a["data-url"]).rsplit("/", maxsplit=1)[-1].split(".")[0]

        if nom_fichier.isdigit():  # Vérification qu'il s'agit d'un numéro
            return nom_fichier
    return None


def extract_numero_bulletin(contenu_soup: BeautifulSoup) -> Optional[str]:
    """
    Extrait le numéro du bulletin à partir du contenu HTML.

    :param contenu_soup: L'objet BeautifulSoup représentant le contenu HTML.
    :return: Le numéro du bulletin ou None si non trouvé.
    """
    if not isinstance(contenu_soup, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    titre_complet = contenu_soup.find("title")
    if titre_complet:
        texte_titre = titre_complet.get_text(strip=True)
        if ">" in texte_titre:
            # Récupération du texte après le premier '>' dans la balise <title>
            numero_bulletin_complet = texte_titre.split(">")[1]
            # Extraction du dernier élément (numéro seulement)
            numero_bulletin = numero_bulletin_complet.split()[-1].strip()

            if numero_bulletin.isdigit():  # Vérification qu'il s'agit d'un numéro
                return numero_bulletin
    return None


def extract_date(contenu_soup: BeautifulSoup) -> Optional[str]:
    """
    Extrait la date de l'article à partir du contenu HTML.

    :param contenu_soup: L'objet BeautifulSoup représentant le contenu HTML.
    :return: La date de l'article ou None si non trouvée.
    """
    if not isinstance(contenu_soup, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    titre_complet = contenu_soup.find("title")
    if titre_complet:
        # Récupération du texte avant ">" dans la balise <title>
        texte_titre = titre_complet.get_text(strip=True)
        if ">" in texte_titre:
            date_str = texte_titre.split(">")[0].strip()
            try:
                # Date sous le format attendu
                date_formate = datetime.strptime(date_str, "%Y/%m/%d").strftime(
                    "%d/%m/%Y"
                )
                return date_formate
            except ValueError:
                return None
    return None


def extract_rubrique(contenu_soup: BeautifulSoup) -> Optional[str]:
    """
    Extrait la rubrique de l'article à partir du contenu HTML.

    :param contenu_soup: L'objet BeautifulSoup représentant le contenu HTML.
    :return: La rubrique de l'article ou None si non trouvée.
    """
    if not isinstance(contenu_soup, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    span42_tags: List[Tag] = [
        tag
        for tag in contenu_soup.find_all("span", {"class": "style42"})
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


def extract_titre(contenu_soup: BeautifulSoup) -> Optional[str]:
    """
    Extrait le titre de l'article à partir du contenu HTML.

    :param contenu_soup: L'objet BeautifulSoup représentant le contenu HTML.
    :return: Le titre de l'article ou None si non trouvé.
    """
    if not isinstance(contenu_soup, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    titre_complet = contenu_soup.find("title")
    if titre_complet:
        # Récupération de la troisième partie après le deuxième ">" dans la balise <title>
        return titre_complet.text.split(">")[2].strip()
    return None


def extract_auteur(contenu_soup: BeautifulSoup) -> Optional[str]:
    """
    Extrait le nom du rédacteur à partir du contenu HTML.

    :param contenu_soup: L'objet BeautifulSoup représentant le contenu HTML.
    :return: Le nom du rédacteur ou None si non trouvé.
    """
    if not isinstance(contenu_soup, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    tr_parent = None
    # Recherche du tableau <tr> contenant le nom du rédacteur
    tr_tags: List[Tag] = [
        tag for tag in contenu_soup.find_all("tr") if isinstance(tag, Tag)
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
            texte_auteur = span_95.get_text(strip=True)
            match = re.search(
                r"ADIT\s*-\s*([A-Za-zÀ-ÿ0-9]+(?:[-'\s][A-Za-zÀ-ÿ0-9]+)*)\s*-.*",
                texte_auteur,
            )
            if match:
                return match.group(1).strip()  # Retourne le nom du rédacteur
    return None


def extract_texte(contenu_soup: BeautifulSoup) -> Optional[str]:
    """
    Extrait le texte à partir du contenu HTML.

    :param contenu_soup: L'objet beautifulsoup représentant le contenu HTML.
    :return: Une liste contenant le texte extrait ou none si non trouvé.
    """
    if not isinstance(contenu_soup, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    parent: List[Tag] = [
        tag
        for tag in contenu_soup.find_all(
            "td", {"class": "FWExtra2", "bgcolor": "#f3f5f8"}
        )
        if isinstance(tag, Tag)
    ]
    texte = parent[0].find_all("span", {"class": "style95"})
    contenu = ""
    if texte:
        for txt in texte:
            texte_clean = txt.get_text().replace("\n", "")
            contenu += " " + texte_clean
        return contenu.strip()
    return None


def extract_images(contenu_soup: BeautifulSoup) -> List[Tuple[str, str]]:
    """
    Extrait les images (sources et légendes) à partir du contenu HTML.

    :param contenu_soup: L'objet BeautifulSoup représentant le contenu HTML.
    :return: Une liste contenant les tuples (lien, légende) des images.
    """

    if not isinstance(contenu_soup, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    images = []
    parents: List[Tag] = [
        tag
        for tag in contenu_soup.find_all(
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
            legende = ""
            span = div.find("span", {"class": "style21"})
            if span:
                legende = span.get_text(strip=True)
            images.append((img_src, legende))

    return images


def extract_contacts(contenu_soup: BeautifulSoup) -> Optional[str]:
    """
    Extrait les contacts à partir du contenu HTML.

    :param contenu_soup: L'objet BeautifulSoup représentant le contenu HTML.
    :return: Une liste de contacts extraits ou une liste vide si aucun contact n'est trouvé.
    """
    if not isinstance(contenu_soup, BeautifulSoup):
        raise ValueError("L'argument entré doit être une instance de BeautifulSoup.")

    td_parent = None
    # On récupère le <td> qui précède celui qu'on cherche
    spans: List[Tag] = [
        tag
        for tag in contenu_soup.find_all("span", {"class": "style28"})
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


def check_global(verbose=False) -> bool:
    """
    Fonction pour vérifier toutes les étapes de l'extraction.
    :param verbose: Affiche tout le contenu extrait si mis à True.
    :return: Un booléen indiquant si tout s'est bien passé.
    """
    est_ok = True
    dossier = unzip_data("../BULLETINS.zip", "data")
    fichiers = [
        os.path.join(dossier, f)
        for f in os.listdir(dossier)
        if os.path.isfile(os.path.join(dossier, f))
    ]

    for chemin_fichier in tqdm(fichiers, desc="Vérification des n° de fichier"):
        soup = open_file(chemin_fichier)
        nom_fichier = extract_nom_fichier(soup)
        if not nom_fichier:
            print(
                f"Erreur: {os.path.basename(chemin_fichier)} ne contient pas de nom valide."
            )
            est_ok = False
        elif verbose:
            print(nom_fichier)

    for chemin_fichier in tqdm(fichiers, desc="Vérification des n° de bulletin"):
        soup = open_file(chemin_fichier)
        numero_bulletin = extract_numero_bulletin(soup)
        if not numero_bulletin:
            print(
                f"Erreur: {os.path.basename(chemin_fichier)} ne contient pas "
                f"de n° de bulletin valide."
            )
            est_ok = False
        elif verbose:
            print(numero_bulletin)

    for chemin_fichier in tqdm(fichiers, desc="Vérification des dates"):
        soup = open_file(chemin_fichier)
        date = extract_date(soup)
        if not date:
            print(
                f"Erreur: {os.path.basename(chemin_fichier)} ne contient pas de date valide."
            )
            est_ok = False
        elif verbose:
            print(date)

    for chemin_fichier in tqdm(fichiers, desc="Vérification des rubriques"):
        soup = open_file(chemin_fichier)
        rubrique = extract_rubrique(soup)
        if not rubrique:
            print(
                f"Erreur: {os.path.basename(chemin_fichier)} ne contient pas de rubrique valide."
            )
            est_ok = False
        elif verbose:
            print(rubrique)

    for chemin_fichier in tqdm(fichiers, desc="Vérification des titres"):
        soup = open_file(chemin_fichier)
        titre = extract_titre(soup)
        if not titre:
            print(f"Erreur: {os.path.basename(chemin_fichier)} ne contient pas de titre.")
            est_ok = False
        elif verbose:
            print(titre)

    for chemin_fichier in tqdm(fichiers, desc="Vérification des auteurs"):
        soup = open_file(chemin_fichier)
        auteur = extract_auteur(soup)
        if not auteur:
            print(
                f"Erreur: {os.path.basename(chemin_fichier)} ne contient "
                f"pas de nom de rédacteur valide."
            )
            est_ok = False
        elif verbose:
            print(auteur)

    for chemin_fichier in tqdm(fichiers, desc="Vérification des contenus"):
        soup = open_file(chemin_fichier)
        texte = extract_texte(soup)
        if not texte:
            print(
                f"Erreur: {os.path.basename(chemin_fichier)} ne contient pas de texte valide."
            )
            est_ok = False
        elif verbose:
            print(texte)

    for chemin_fichier in tqdm(fichiers, desc="Vérification des images"):
        soup = open_file(chemin_fichier)
        images = extract_images(soup)
        if verbose:
            pprint.pprint(images)

    for chemin_fichier in tqdm(fichiers, desc="Vérification des contacts"):
        soup = open_file(chemin_fichier)
        contacts = extract_contacts(soup)
        if not contacts:
            print(f"Erreur: {os.path.basename(chemin_fichier)} ne contient pas de contact.")
            est_ok = False
        elif verbose:
            print(contacts)

    return est_ok


def genere_article(fichier: str) -> Optional[Element]:
    """
    Génère un article au format XML

    :param fichier: Le fichier HTML à traiter.
    :return: Une chaîne XML représentant l'article.
    """
    try:
        soup = open_file(fichier)

        # Création de l'élément XML principal
        article = ET.Element("article")

        # Ajout des sous-éléments à l'article en utilisant les fonctions d'extraction
        ET.SubElement(article, "fichier").text = extract_nom_fichier(soup)
        ET.SubElement(article, "numero").text = extract_numero_bulletin(soup)
        ET.SubElement(article, "date").text = extract_date(soup)
        ET.SubElement(article, "rubrique").text = extract_rubrique(soup)
        ET.SubElement(article, "titre").text = extract_titre(soup)
        ET.SubElement(article, "auteur").text = extract_auteur(soup)
        ET.SubElement(article, "texte").text = extract_texte(soup)

        images = extract_images(soup)
        images_elem = ET.SubElement(article, "images")
        # 'images' est une liste dont chaque élément devient une image
        for url, legende in images:
            image_elem = ET.SubElement(images_elem, "image")
            ET.SubElement(image_elem, "urlImage").text = url.strip()
            ET.SubElement(image_elem, "legendeImage").text = legende.strip()

        ET.SubElement(article, "contact").text = extract_contacts(soup)

        return article

    except Exception as e:
        print(f"Erreur lors de la génération de l'article avec {fichier} : {e}")
        return None


def genere_corpus(dossier_zip: str, fichier_sortie: str) -> None:
    """
    Génère un corpus au format XML et l'enregistre dans un fichier.

    :param dossier_zip: Le répertoire contenant le fichier ZIP à traiter.
    :param fichier_sortie: Le fichier où le corpus XML sera sauvegardé.
    :return: None.
    """
    try:
        repertoire = unzip_data(dossier_zip, "/..")
        corpus = ET.Element("corpus")

        for element in tqdm(os.listdir(repertoire), desc="Genération du corpus"):
            chemin_fichier = os.path.join(repertoire, element)
            if os.path.isfile(chemin_fichier):
                article = genere_article(chemin_fichier)
                if article is not None:
                    corpus.append(article)
                else:
                    raise ValueError(
                        f"Impossible de générer l'article pour {chemin_fichier}"
                    )

        # Utilisation de minidom pour avoir des indentations
        xml_str = minidom.parseString(ET.tostring(corpus)).toprettyxml(indent="  ")

        # Sauvegarde du contenu dans un fichier
        with open(fichier_sortie, "w", encoding="utf-8") as file:
            file.write(xml_str)
            print(f"Corpus généré avec succès dans: {fichier_sortie}")

    except FileNotFoundError as fnf_error:
        print(
            f"Erreur: fichier ou répertoire spécifié non trouvé. Détails: {fnf_error}"
        )
    except Exception as e:
        print(f"Erreur: lors de la génération du corpus: {e}")


if __name__ == "__main__":
    if check_global():
        genere_corpus("../BULLETINS.zip", "data/corpus.xml")
    else:
        print("Problème durant la vérification des fichiers !")
