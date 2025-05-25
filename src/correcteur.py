"""
Fonctions permettant la correction orthographique à partir du corpus.
"""

import pandas as pd
import numpy as np
from utils import tokenize


def recherche_prefixe(
    mot1: str, mot2: str, seuil_min: float, seuil_max: float, seuil_proximite: float
) -> float:
    """
    Recherche la proximité entre deux mots en fonction de leur préfixe commun.

    La fonction compare les deux mots caractère par caractère et retourne un pourcentage
    basé sur la longueur du préfixe commun.

    :param mot1: Le premier mot à comparer.
    :param mot2: Le deuxième mot à comparer.
    :param seuil_min: Le seuil minimal pour filtrer les mots trop courts.
    :param seuil_max: Le seuil maximal de différence de longueur entre les deux mots.
    :param seuil_proximite: Le seuil de proximité (en %) pour valider la correspondance.
    :return: Pourcentage de proximité entre les deux mots si le seuil est dépassé, sinon 0
    """
    # Vérifie si l'un des mots est trop court
    if (len(mot1) < seuil_min) or (len(mot2) < seuil_min):
        return 0

    # Vérifie si la différence de longueur des mots est trop grande
    if abs(len(mot1) - len(mot2)) > seuil_max:
        return 0

    # Comparaison des mots caractère par caractère jusqu'à la première différence
    compteur = 0
    while compteur < min(len(mot1), len(mot2)) and mot1[compteur] == mot2[compteur]:
        compteur += 1

    # Calcule la proximité en pourcentage
    proximite = (compteur / max(len(mot1), len(mot2))) * 100

    # Vérifie si la proximité dépasse le seuil
    if proximite >= seuil_proximite:
        return proximite
    return 0


def levenshtein(mot1: str, mot2: str) -> int:
    """
    Calcule la distance de Levenshtein entre deux chaînes de caractères.
    La distance de Levenshtein est une mesure du nombre d'opérations
    (insertion, suppression, ou substitution) à réaliser pour passer d'un mot à un autre.

    :param mot1: La première chaîne de caractères.
    :param mot2: La deuxième chaîne de caractères.
    :return: La distance de Levenshtein entre mot1 et mot2.
    """

    # Initialisation de la matrice de distance
    distance = np.zeros((len(mot1) + 1, len(mot2) + 1))

    # Initialisation des bords de la matrice (cas de transformation d'une chaîne vide en une autre)
    distance[0, 0] = 0
    for i in range(0, len(mot1) + 1):
        distance[i, 0] = i
    for j in range(0, len(mot2) + 1):
        distance[0, j] = j

    # Remplissage de la matrice avec les valeurs minimales des transformations possibles
    for i in range(1, len(mot1) + 1):
        for j in range(1, len(mot2) + 1):
            if mot1[i - 1] == mot2[j - 1]:
                # Si les caractères sont =, on prend le minimum des trois opérations possibles
                distance[i, j] = min(
                    distance[i - 1, j - 1],
                    distance[i, j - 1] + 1,
                    distance[i - 1, j] + 1,
                )
            else:
                # Si les caractères sont !=, on choisit l'opération la moins coûteuse
                distance[i, j] = min(
                    distance[i - 1, j - 1] + 1,
                    distance[i, j - 1] + 1,
                    distance[i - 1, j] + 1,
                )

    # La distance de Levenshtein est la valeur en bas à droite de la matrice
    return int(distance[len(mot1), len(mot2)])


def correcteur_orthographique(
    input_texte: str,
    lexique: str,
    seuil_min: float,
    seuil_max: float,
    seuil_proximite: float,
) -> str:
    """
    Cette fonction traite un texte en le tokenisant et en recherchant chaque mot
    dans le lexique pour en obtenir le lemme.
    Si un mot n'est pas dans le lexique, la fonction tente de trouver des mots proches
    à l'aide de la proximité de préfixe et de la distance de Levenshtein.

    :param input_texte: Texte à corriger sous forme de chaîne de caractères.
    :param lexique: Fichier contenant un lexique au format (mot → lemme).
    :param seuil_min: Le seuil minimal pour la recherche par préfixe.
    :param seuil_max: Le seuil maximal pour la recherche par préfixe.
    :param seuil_proximite: Le seuil de proximité pour la recherche par préfixe.
    :return: Texte corrigé sous forme de chaîne de caractères
    """

    # Initialisation des variables
    output_liste = []
    lexique_dataframe = pd.read_csv(
        lexique, sep="→", header=None, names=["mot", "lemme"], engine="python"
    )

    for mot in tokenize(input_texte):
        match = lexique_dataframe[lexique_dataframe["mot"] == mot]
        # Si le mot existe dans le lexique, ajoute son lemme
        if not match.empty:
            output_liste.append(match.iloc[0]["lemme"])

        # Si le mot n'est pas dans le lexique, recherche de candidats proches
        else:
            candidats = []
            for candidat_potentiel in lexique_dataframe["mot"]:
                proximite = recherche_prefixe(
                    mot, candidat_potentiel, seuil_min, seuil_max, seuil_proximite
                )
                if proximite != 0:
                    candidats.append((candidat_potentiel, proximite))

            # Si aucun candidat trouvé, ajouter None
            if len(candidats) == 0:
                output_liste.append(mot)
                print(f"Aucun candidat trouvé pour le mot '{mot}'")
            else:
                # Trouver le candidat avec la meilleure proximité
                max_proximite = max(c[1] for c in candidats)
                meilleur_candidats = [c for c in candidats if c[1] == max_proximite]

                # Si plusieurs candidats ont la même proximité,
                # choisir celui avec la distance de Levenshtein la plus faible
                if len(meilleur_candidats) == 1:
                    output_liste.append(
                        lexique_dataframe[
                            lexique_dataframe["mot"] == meilleur_candidats[0][0]
                        ].iloc[0]["lemme"]
                    )
                else:
                    # Utilisation de la distance de Levenshtein pour choisir le meilleur candidat
                    meilleur_candidat_lev = min(
                        meilleur_candidats, key=lambda x: levenshtein(mot, x[0])
                    )
                    output_liste.append(
                        lexique_dataframe[
                            lexique_dataframe["mot"] == meilleur_candidat_lev[0]
                        ].iloc[0]["lemme"]
                    )
    # Retour du texte corrigé
    return " ".join(output_liste)


if __name__ == "__main__":
    TEXTE = "etudia en nanotechnolojies"
    TEXTE_CORRIGE = correcteur_orthographique(
        TEXTE, "data/lemma_stemmer.txt", 3, 12, 60
    )
    print(TEXTE_CORRIGE)
