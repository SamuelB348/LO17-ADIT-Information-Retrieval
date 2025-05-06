import tkinter as tk
from tkinter import ttk
import datetime
from tkinter import PhotoImage

resultats = [
    {'id': 1, 'titre': 'Recherche sur l\'IA', 'date': '2025-04-28', 'rubrique': 'Technologie', 'extrait': 'L\'intelligence artificielle est un domaine en pleine expansion.'},
    {'id': 2, 'titre': 'Histoire de l\'informatique', 'date': '2020-06-15', 'rubrique': 'Informatique', 'extrait': 'L\'informatique a révolutionné le monde moderne, de la machine à calculer à l\'ordinateur personnel.'},
    {'id': 3, 'titre': 'Nanotechnologies et leurs applications', 'date': '2023-09-12', 'rubrique': 'Science', 'extrait': 'Les nanotechnologies promettent de grandes avancées dans la médecine, l\'énergie et la fabrication.'},
]

def trier_resultats():
    query = search_entry.get()
    critere_tri = tri_var.get()

    if query:
        filtered_results = [res for res in resultats if query.lower() in res['titre'].lower()]
    else:
        filtered_results = resultats

    if critere_tri == 'Pertinence':
        filtered_results.sort(key=lambda x: x['date'], reverse=True)
    elif critere_tri == 'Date Croissante':
        filtered_results.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%Y-%m-%d'))
    elif critere_tri == 'Date Décroissante':
        filtered_results.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)

    afficher_resultats(filtered_results)

def afficher_resultats(filtered_results):
    for row in tree.get_children():
        tree.delete(row)

    for resultat in filtered_results:
        tree.insert("", "end", values=(resultat['id'], resultat['titre'], resultat['date'], resultat['rubrique'], resultat['extrait']))

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

icon = PhotoImage(file='icon.png')
root.iconphoto(False, icon)

frame_resultats = ttk.Frame(root, style="TFrame")
frame_resultats.pack(pady=20, fill="both", expand=True)

tree = ttk.Treeview(frame_resultats, columns=("ID", "Titre", "Date", "Rubrique", "Extrait"), show="headings")
tree.pack(fill="both", expand=True)

tree.heading("ID", text="ID")
tree.heading("Titre", text="Titre")
tree.heading("Date", text="Date")
tree.heading("Rubrique", text="Rubrique")
tree.heading("Extrait", text="Extrait")

tree.column("ID", width=50, anchor="center")
tree.column("Titre", width=200, anchor="w")
tree.column("Date", width=100, anchor="center")
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
