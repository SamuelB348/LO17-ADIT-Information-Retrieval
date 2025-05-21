"""
Interface utilisateur.
"""

import os
import threading
import datetime
import webbrowser
import tkinter as tk
import customtkinter as ctk
from browser import moteur
from utils import parse_xml

# Initialisation de CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("LO17 : Indexation et Recherche d’information")
root.geometry("1200x700")
root.configure(fg_color="#A9D8FF")
icon = tk.PhotoImage(file="images/icon.png")
root.wm_iconbitmap("images/icon.ico")

custom_font = ctk.CTkFont(family="Segoe UI")


def trier_resultats():
    """
    Description.
    :return:
    """
    query = search_entry.get()
    query = query.replace("’", " ' ")
    query = query.replace("'", " ' ")
    critere_tri = tri_var.get()

    # Affiche immédiatement le message d'attente
    afficher_resultats(["Veuillez patienter..."], "bulletin")

    # Lancer le traitement dans un thread pour ne pas bloquer l'UI
    threading.Thread(
        target=trier_resultats_threaded, args=(query, critere_tri), daemon=True
    ).start()


def trier_resultats_threaded(query, critere_tri):
    """
    Description.
    :param query:
    :param critere_tri:
    :return:
    """
    doc_type = None
    root_corpus = parse_xml("data/corpus.xml")

    if query:
        resultats, doc_type = moteur(query)

        if doc_type == "article":
            resultats_structured = []
            if resultats:
                for result in resultats:
                    for article in root_corpus.findall(".//article"):
                        fichier = article.find("fichier")
                        if fichier is not None and fichier.text == result:
                            target_article = article
                            break
                    dico = {
                        "id": result,
                        "titre": target_article.find("titre").text,
                        "date": target_article.find("date").text,
                        "numero": target_article.find("numero").text,
                        "rubrique": target_article.find("rubrique").text,
                        "extrait": " ".join(
                            target_article.find("texte").text.split()[:50]
                        )
                        + "...",
                    }
                    resultats_structured.append(dico)
                filtered_results = resultats_structured
            else:
                filtered_results = []
        elif doc_type in ["bulletin", "rubrique"]:
            filtered_results = list(resultats)
        else:
            filtered_results = []

        if doc_type == "article":
            if critere_tri == "Pertinence" and filtered_results:
                filtered_results.sort(key=lambda x: x["date"], reverse=True)
            elif critere_tri == "Date Croissante":
                filtered_results.sort(
                    key=lambda x: datetime.datetime.strptime(x["date"], "%d/%m/%Y")
                )
            elif critere_tri == "Date Décroissante":
                filtered_results.sort(
                    key=lambda x: datetime.datetime.strptime(x["date"], "%d/%m/%Y"),
                    reverse=True,
                )
    else:
        filtered_results = []
        doc_type = "bulletin"  # fallback type for placeholder

    # Afficher les résultats après traitement
    afficher_resultats(filtered_results, doc_type)


def afficher_resultats(filtered_results, doc_type):
    """
    Description.
    :param filtered_results:
    :param doc_type:
    :return:
    """
    # Clear previous widgets
    for widget in scrollable_resultats.winfo_children():
        widget.destroy()

    if doc_type == "article":
        # Header row
        headers = [
            "ID",
            "Titre",
            "Date",
            "N° de bulletin",
            "Rubrique",
            "Extrait",
            "Consulter",
        ]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                scrollable_resultats,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                anchor="center",
            )
            label.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

        for row_index, resultat in enumerate(filtered_results, start=1):
            ctk.CTkLabel(scrollable_resultats, text=resultat["id"]).grid(
                row=row_index, column=0, padx=5, pady=2, sticky="nsew"
            )
            ctk.CTkLabel(
                scrollable_resultats, text=resultat["titre"], wraplength=200
            ).grid(row=row_index, column=1, padx=5, pady=2, sticky="nsew")
            ctk.CTkLabel(scrollable_resultats, text=resultat["date"]).grid(
                row=row_index, column=2, padx=5, pady=2, sticky="nsew"
            )
            ctk.CTkLabel(scrollable_resultats, text=resultat["numero"]).grid(
                row=row_index, column=3, padx=5, pady=2, sticky="nsew"
            )
            ctk.CTkLabel(scrollable_resultats, text=resultat["rubrique"]).grid(
                row=row_index, column=4, padx=5, pady=2, sticky="nsew"
            )
            ctk.CTkLabel(
                scrollable_resultats,
                text=resultat["extrait"],
                wraplength=400,
                anchor="w",
                justify="left",
            ).grid(row=row_index, column=5, padx=5, pady=2, sticky="nsew")

            ouvrir_button = ctk.CTkButton(
                scrollable_resultats,
                text="Ouvrir",
                width=60,
                height=28,
                command=lambda id=resultat["id"]: ouvrir_fichier(id),
            )
            ouvrir_button.grid(row=row_index, column=6, padx=5, pady=2)

    elif doc_type in ["rubrique", "bulletin"]:
        for i, item in enumerate(filtered_results):
            label = ctk.CTkLabel(
                scrollable_resultats, text=item, font=ctk.CTkFont(size=14), anchor="w"
            )
            label.pack(fill="x", padx=10, pady=4)


def ouvrir_fichier(id_value):
    """
    Description.
    :param id_value:
    :return:
    """
    fichier_path = os.path.join("data", "BULLETINS", f"{id_value}.htm")
    if os.path.exists(fichier_path):
        webbrowser.open_new_tab(fichier_path)
    else:
        print(f"Fichier non trouvé : {fichier_path}")


# Titre
title_label = ctk.CTkLabel(
    root,
    text="Bienvenue sur le moteur de recherche de l'ADIT",
    font=("Helvetica", 25, "bold"),
    text_color="navy",
)
title_label.pack(pady=20)

# Zone de recherche
search_frame = ctk.CTkFrame(root, fg_color="#A9D8FF")
search_frame.pack(pady=10, padx=0)

search_entry = ctk.CTkEntry(search_frame, width=400)
search_entry.grid(row=0, column=0, padx=(0, 10), sticky="w")

search_button = ctk.CTkButton(search_frame, text="Rechercher", command=trier_resultats)
search_button.grid(row=0, column=1, padx=(10, 0), sticky="w")

# Tri
tri_frame = ctk.CTkFrame(root, fg_color="#A9D8FF")
tri_frame.pack(anchor="ne", padx=20, pady=5)

tri_label = ctk.CTkLabel(tri_frame, text="Trier par :")
tri_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

tri_var = ctk.StringVar(value="Pertinence")
tri_menu = ctk.CTkComboBox(
    tri_frame,
    variable=tri_var,
    values=["Pertinence", "Date Croissante", "Date Décroissante"],
    width=200,
)
tri_menu.grid(row=0, column=1)

# Résultats
resultats_frame = ctk.CTkFrame(root)
resultats_frame.pack(fill="both", expand=True, padx=20, pady=10)

scrollable_resultats = ctk.CTkScrollableFrame(resultats_frame, height=450)
scrollable_resultats.pack(fill="both", expand=True)
for col_index in range(7):
    scrollable_resultats.grid_columnconfigure(col_index, weight=1)

# Lancement
root.mainloop()
