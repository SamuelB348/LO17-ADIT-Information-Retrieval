"""
Interface utilisateur.
"""

import os
import threading
import datetime
import webbrowser
import tkinter as tk
import customtkinter as ctk
from moteur import moteur
from utils import parse_xml


class RechercheApp:
    """
    Interface utilisateur.
    """

    def __init__(self):
        # Initialisation de l'interface
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("LO17 : Indexation et Recherche d’information")
        self.root.geometry("1200x700")
        self.root.configure(fg_color="#A9D8FF")
        self.root.iconphoto(False, tk.PhotoImage(file="images/icon.png"))
        self.root.wm_iconbitmap("images/icon.ico")

        self.tri_var = tk.StringVar(value="Classique")

        self.build_interface()
        self.root.mainloop()

    def build_interface(self):
        """
        Construit l'interface graphique.
        :return: None
        """
        # Titre
        ctk.CTkLabel(
            self.root,
            text="Bienvenue sur le moteur de recherche de l'ADIT",
            font=("Helvetica", 25, "bold"),
            text_color="navy",
        ).pack(pady=20)

        # Zone de recherche
        search_frame = ctk.CTkFrame(self.root, fg_color="#A9D8FF")
        search_frame.pack(pady=10)

        self.search_entry = ctk.CTkEntry(search_frame, width=400)
        self.search_entry.grid(row=0, column=0, padx=(0, 10))

        search_button = ctk.CTkButton(
            search_frame, text="Rechercher", command=self.trier_resultats
        )
        search_button.grid(row=0, column=1)

        # Menu tri
        tri_frame = ctk.CTkFrame(self.root, fg_color="#A9D8FF")
        tri_frame.pack(anchor="ne", padx=20, pady=5)

        ctk.CTkLabel(tri_frame, text="Trier par :").grid(row=0, column=0, padx=(0, 10))
        ctk.CTkComboBox(
            tri_frame,
            variable=self.tri_var,
            values=["Classique", "Date Croissante", "Date Décroissante"],
            width=200,
        ).grid(row=0, column=1)

        # Résultats
        resultats_frame = ctk.CTkFrame(self.root)
        resultats_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.scrollable_resultats = ctk.CTkScrollableFrame(resultats_frame, height=450)
        self.scrollable_resultats.pack(fill="both", expand=True)
        for col_index in range(7):
            self.scrollable_resultats.grid_columnconfigure(col_index, weight=1)

    def trier_resultats(self):
        """
        Lance la fonction trier_resultats_threaded, ce qui permet
        d'afficher "Veuillez patienter" en attendant les résultats.
        :return: None
        """
        query = self.search_entry.get().replace("’", " ' ").replace("'", " ' ")
        critere_tri = self.tri_var.get()

        self.afficher_resultats(["Veuillez patienter..."], "bulletin")
        threading.Thread(
            target=self.trier_resultats_threaded,
            args=(query, critere_tri),
            daemon=True,
        ).start()

    def trier_resultats_threaded(self, query, critere_tri):
        """
        Lance le moteur et tri les résultats selon le critère choisi par
        l'utilisateur.
        :param query: La requête entrée par l'utilisateur.
        :param critere_tri: Le critère de tri.
        :return: None
        """
        doc_type = None
        root_corpus = parse_xml("data/corpus.xml")
        filtered_results = []

        if query:
            resultats, doc_type = moteur(query)
            if doc_type == "article":
                resultats_structured = []
                for result in resultats:
                    for article in root_corpus.findall(".//article"):
                        fichier = article.find("fichier")
                        if fichier is not None and fichier.text == result:
                            dico = {
                                "id": result,
                                "titre": article.find("titre").text,
                                "date": article.find("date").text,
                                "numero": article.find("numero").text,
                                "rubrique": article.find("rubrique").text,
                                "extrait": " ".join(
                                    article.find("texte").text.split()[:50]
                                )
                                + "...",
                            }
                            resultats_structured.append(dico)
                            break
                filtered_results = resultats_structured
            elif doc_type in ["bulletin", "rubrique"]:
                filtered_results = list(resultats)

            if doc_type == "article":
                if critere_tri == "Classique":
                    filtered_results.sort(key=lambda x: x["date"], reverse=True)
                elif "Croissante" in critere_tri:
                    filtered_results.sort(
                        key=lambda x: datetime.datetime.strptime(x["date"], "%d/%m/%Y")
                    )
                elif "Décroissante" in critere_tri:
                    filtered_results.sort(
                        key=lambda x: datetime.datetime.strptime(x["date"], "%d/%m/%Y"),
                        reverse=True,
                    )
        else:
            doc_type = "bulletin"

        self.afficher_resultats(filtered_results, doc_type)

    def afficher_resultats(self, filtered_results, doc_type):
        """
        Affiche les résultats dans une structure de tableau.
        :param filtered_results: Les résultats filtrés par la méthode précédente.
        :param doc_type: Le type de document qui a été renvoyé.
        :return: None
        """
        for widget in self.scrollable_resultats.winfo_children():
            widget.destroy()

        if doc_type == "article":
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
                ctk.CTkLabel(
                    self.scrollable_resultats,
                    text=header,
                    font=ctk.CTkFont(weight="bold"),
                ).grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

            for row_index, resultat in enumerate(filtered_results, start=1):
                ctk.CTkLabel(self.scrollable_resultats, text=resultat["id"]).grid(
                    row=row_index, column=0, padx=5, pady=2, sticky="nsew"
                )
                ctk.CTkLabel(
                    self.scrollable_resultats, text=resultat["titre"], wraplength=200
                ).grid(row=row_index, column=1, padx=5, pady=2, sticky="nsew")
                ctk.CTkLabel(self.scrollable_resultats, text=resultat["date"]).grid(
                    row=row_index, column=2, padx=5, pady=2, sticky="nsew"
                )
                ctk.CTkLabel(self.scrollable_resultats, text=resultat["numero"]).grid(
                    row=row_index, column=3, padx=5, pady=2, sticky="nsew"
                )
                ctk.CTkLabel(self.scrollable_resultats, text=resultat["rubrique"]).grid(
                    row=row_index, column=4, padx=5, pady=2, sticky="nsew"
                )
                ctk.CTkLabel(
                    self.scrollable_resultats,
                    text=resultat["extrait"],
                    wraplength=400,
                    anchor="w",
                    justify="left",
                ).grid(row=row_index, column=5, padx=5, pady=2, sticky="nsew")

                ctk.CTkButton(
                    self.scrollable_resultats,
                    text="Ouvrir",
                    width=60,
                    height=28,
                    command=lambda id=resultat["id"]: self.ouvrir_fichier(id),
                ).grid(row=row_index, column=6, padx=5, pady=2)
        else:
            for i, item in enumerate(filtered_results):
                ctk.CTkLabel(
                    self.scrollable_resultats, text=item, font=ctk.CTkFont(size=14)
                ).pack(fill="x", padx=10, pady=4)

    def ouvrir_fichier(self, id_value):
        """
        Permet d'ouvrir les fichiers .htm sur un navigateur.
        :param id_value: L'ID du document à ouvrir.
        :return: None
        """
        fichier_path = os.path.join("data", "BULLETINS", f"{id_value}.htm")
        if os.path.exists(fichier_path):
            webbrowser.open_new_tab(fichier_path)
        else:
            print(f"Fichier non trouvé : {fichier_path}")
