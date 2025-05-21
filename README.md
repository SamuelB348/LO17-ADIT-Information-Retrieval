# LO17-ADIT-Information-Retrieval


## Description du projet

Ce projet est un système de recherche d'information développé dans le cadre du cours LO17 à l'ADIT. Il permet d'effectuer des recherches sur un corpus de bulletins avec une interface graphique intuitive, basée sur Tkinter.

---

## Organisation du projet

À la racine du projet, on trouve :

- `bulletin.zip` : archive contenant les données initiales.
- `.gitignore` : fichier de gestion des fichiers à ignorer par Git.
- `requirements.txt` : liste des dépendances Python nécessaires au projet.
- `src/` : dossier principal contenant les scripts Python du projet.
- `images/` : dossier contenant les images utilisées, notamment `icon.png` pour l’interface.
- `data/` : dossier contenant les fichiers générés par le projet.
- `data/initia/` : sous-dossier avec les bulletins initiaux et leurs images associées.

---

### Contenu du dossier `src/`

Ce dossier contient les différentes fonctions et scripts, qui peuvent être lancés séparément pour tester chaque étape du projet :

- `anti_dictionnaire.py` (ou `anti_dictionnaire.py`)  
- `data_parser.py`  
- `interface.py`  
- `inverted_index.py`  
- `lemmatize.py`  
- `segmente.py`  
- `spellchecker.py`  
- `substitue.py`  
- `traitement_requete.py`  
- `moteur.py`  
- `utils.py`  

---

## Installation

Avant de lancer le projet, il est nécessaire d'installer les dépendances Python. Celles-ci sont listées dans le fichier `requirements.txt`.

Pour installer les modules requis, exécutez la commande suivante dans votre terminal :

```bash
pip install -r requirements.txt
