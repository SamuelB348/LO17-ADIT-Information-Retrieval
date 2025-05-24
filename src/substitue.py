"""
Fichier permettant de substituer un mot par un autre dans un texte.
"""

from typing import List
import pandas as pd
import numpy as np


def substitue_texte(input_texte: str | List[str], fichier_subs: str) -> str:
    """
    Remplace ou élimine des mots dans un texte en fonction d'un fichier de substitution.

    :param input_texte: Le texte (chaîne de caractères) ou liste de tokens à traiter.
    :param fichier_subs: Le chemin du fichier qui contient les mots à remplacer et leurs substituts.
    :return: Une chaîne de caractères où les mots ont été remplacés ou éliminés.
    """
    if isinstance(input_texte, str):
        input_texte = (
            input_texte.split()
        )  # Découpe le texte en tokens (si c'est une str)

    # Lecture du fichier de substitution en format pandas (deux colonnes : token, substitute)
    subs_df = pd.read_csv(
        fichier_subs, sep="\t", header=None, names=["token", "substitute"]
    )
    # Remplacement des valeurs Nan par une chaine vide
    subs_df = subs_df.replace(np.nan, "", regex=True)
    # Remplacement des mots selon le fichier de substitution
    for i, mot in enumerate(input_texte):
        substitut = subs_df.loc[subs_df["token"] == mot, "substitute"]
        # Si le mot a un substitut on le change, sinon on le laisse
        input_texte[i] = substitut.iloc[0] if not substitut.empty else mot

    return " ".join(input_texte)  # Renvoie du texte sous forme de str
