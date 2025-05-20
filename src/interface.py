import tkinter as tk
from tkinter import ttk
import datetime
from tkinter import PhotoImage
from temp import moteur
from utils import parse_xml
import xml.etree.ElementTree as ET


def trier_resultats():
    query = search_entry.get()
    critere_tri = tri_var.get()

    root_corpus = parse_xml('data/corpus.xml')

    if query:
        resultats, doc_type = moteur(query)
        if doc_type == "article":
            resultats_structured = []
            if resultats:
                for result in resultats:
                    for article in root_corpus.findall('.//article'):
                        fichier = article.find('fichier')
                        if fichier is not None and fichier.text == result:
                            target_article = article
                            break
                    dico = {}
                    dico['id'] = result
                    dico['titre'] = target_article.find('titre').text
                    dico['date'] = target_article.find('date').text
                    dico['numero'] = target_article.find('numero').text
                    dico['rubrique'] = target_article.find('rubrique').text
                    dico['extrait'] = " ".join(target_article.find('texte').text.split()[:100]) + "..."
                    resultats_structured.append(dico)
                filtered_results = resultats_structured
            else:
                filtered_results = []
        else:
            filtered_results = []
    else:
        filtered_results = []

    if critere_tri == 'Pertinence' and filtered_results:
        filtered_results.sort(key=lambda x: x['date'], reverse=True)
    elif critere_tri == 'Date Croissante' and filtered_results:
        filtered_results.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%d/%m/%Y'))
    elif critere_tri == 'Date Décroissante' and filtered_results:
        filtered_results.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%d/%m/%Y'), reverse=True)

    afficher_resultats(filtered_results)

def afficher_resultats(filtered_results):
    for row in tree.get_children():
        tree.delete(row)

    for resultat in filtered_results:
        tree.insert("", "end", values=(resultat['id'], resultat['titre'], resultat['date'], resultat['numero'], resultat['rubrique'], resultat['extrait']))

root = tk.Tk()
root.title("LO17 : Indexation et Recherche d’information")
root.geometry("1200x600")
root.configure(bg='#A9D8FF')

title_label = ttk.Label(root, text="Bienvenue sur le moteur de recherche de l'ADIT", font=("Helvetica", 20, "bold"), background="#A9D8FF", foreground="navy")
title_label.pack(pady=20)

search_frame = ttk.Frame(root, style="TFrame")
search_frame.pack(pady=10)

search_label = ttk.Label(search_frame, text="Rechercher : ", font=("Helvetica", 14), background="#A9D8FF", foreground="navy")
search_label.grid(row=0, column=0, padx=10)

search_entry = ttk.Entry(search_frame, width=50, font=("Helvetica", 14))
search_entry.grid(row=0, column=1, padx=10)

style = ttk.Style()
style.configure("TButton", font=("Helvetica", 14), padding=6)

search_button = ttk.Button(search_frame, text="Rechercher", command=trier_resultats, style="TButton")
search_button.grid(row=0, column=2, padx=10)

icon = PhotoImage(file='images/icon.png')
root.iconphoto(False, icon)

frame_resultats = ttk.Frame(root, style="TFrame")
frame_resultats.pack(pady=20, fill="both", expand=True)

tree = ttk.Treeview(frame_resultats, columns=("ID", "Titre", "Date", "N° bulletin", "Rubrique", "Extrait"), show="headings")
tree.pack(fill="both", expand=True)

tree.heading("ID", text="ID")
tree.heading("Titre", text="Titre")
tree.heading("Date", text="Date")
tree.heading("N° bulletin", text="N° bulletin")
tree.heading("Rubrique", text="Rubrique")
tree.heading("Extrait", text="Extrait")

tree.column("ID", width=50, anchor="center")
tree.column("Titre", width=200, anchor="w")
tree.column("Date", width=100, anchor="center")
tree.column("N° bulletin", width=50, anchor="center")
tree.column("Rubrique", width=120, anchor="w")
tree.column("Extrait", width=400, anchor="w")

tree.column("Extrait", width=400, anchor="w", stretch=tk.YES)

frame_tri = ttk.Frame(root, style="TFrame")
frame_tri.pack(side="top", anchor="ne", padx=20, pady=10, fill="x")

tri_var = tk.StringVar(value='Pertinence')

tri_label = ttk.Label(frame_tri, text="Trier par : ", font=("Helvetica", 14), background="#A9D8FF", foreground="navy")
tri_label.grid(row=0, column=0, pady=10)

tri_menu = ttk.Combobox(frame_tri, textvariable=tri_var, values=['Pertinence', 'Date Croissante', 'Date Décroissante'], state="readonly", font=("Helvetica", 14))
tri_menu.grid(row=0, column=1, padx=10)

style.configure("TLabel", font=("Helvetica", 14))
style.configure("TFrame", background="#A9D8FF")

root.mainloop()
