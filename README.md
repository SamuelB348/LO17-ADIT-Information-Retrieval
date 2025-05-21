# LO17-ADIT-Information-Retrieval

## Description

Ce projet est un moteur de recherche d’informations développé dans le cadre du cours LO17 à l’ADIT.  
Il permet d’indexer, traiter et rechercher des articles à partir d’un corpus de bulletins, avec une interface graphique intuitive.

---

## Organisation du projet

À la racine du projet, on trouve :

- `bulletin.zip` : archive contenant les données initiales (bulletins et images associées).
- `.gitignore` : fichier pour exclure certains fichiers du suivi Git.
- `requirements.txt` : liste des dépendances Python nécessaires au projet.
- `src/` : dossier principal contenant tous les scripts Python, organisés pour faciliter le développement et les tests.
- `images/` : contient les icônes utilisées pour l’interface graphique (notamment `icon.png`).
- `data/` : contient tous les fichiers générés lors de l’exécution du projet ainsi que le dossier `initial/` avec les bulletins et images sources.

---

### Structure détaillée du projet

├── bulletin.zip # Archive contenant les bulletins initiaux
├── .gitignore # Fichier Git pour ignorer certains fichiers
├── requirements.txt # Dépendances Python nécessaires
├── src/
│ ├── anti_dictionnaire.py # Filtrage des mots vides
│ ├── data_parser.py # Parsing des données brutes
│ ├── interface.py # Interface graphique (Tkinter)
│ ├── inverted_index.py # Index inversé pour la recherche
│ ├── lemmatize.py # Lemmatisation des termes
│ ├── segmente.py # Segmentation du texte
│ ├── spellchecker.py # Correction orthographique
│ ├── substitue.py # Gestion des synonymes
│ ├── traitement_requete.py # Traitement des requêtes utilisateur
│ ├── moteur.py # Moteur de recherche principal
│ └── utils.py # Fonctions utilitaires
├── data/ # Dossier contenant les données générées
│ ├── initial/ # Bulletins et images d'origine
│ └── (autres fichiers générés)
└── images/
└── icon.png # Icône pour l'interface

## Installation

Avant toute chose, il est nécessaire d’installer les dépendances Python listées dans `requirements.txt`.  
Exécutez la commande suivante dans votre terminal :

```bash
pip install -r requirements.txt
