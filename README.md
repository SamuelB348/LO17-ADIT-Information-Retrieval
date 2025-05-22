# LO17-ADIT-Information-Retrieval

## Description

Ce projet est un moteur de recherche d’informations développé dans le cadre du cours LO17 à l’ADIT.  
Il permet d’indexer, traiter et rechercher des articles à partir d’un corpus de bulletins, avec une interface graphique intuitive.

---

## Organisation du projet

À la racine du projet, on trouve :

- `BULLETINS.zip` : archive contenant les données initiales (bulletins et images associées).
- `.gitignore` : fichier pour exclure certains fichiers du suivi Git.
- `requirements.txt` : liste des dépendances Python nécessaires au projet.
- `src/` : dossier principal contenant tous les scripts Python, organisés pour faciliter le développement et les tests.

Dans le dossier src, on trouve :
- `images/` : contient les icônes utilisées pour l’interface graphique (notamment `icon.png`).
- `data/` : contient tous les fichiers générés lors de l’exécution du projet ainsi que le dossier `initial/` avec les bulletins et images sources.
- les fichiers python du projet

---

### Structure détaillée du projet

/ (racine)  
├── BULLETINS.zip          # Archive contenant les bulletins initiaux  
├── .gitignore             # Fichier Git pour ignorer certains fichiers  
├── requirements.txt       # Liste des dépendances Python  
├── README.md              # Ce fichier readme  
├── src/                   # Dossier principal des scripts et ressources  
│   ├── anti_dictionnary.py    # Filtrage des mots vides  
│   ├── data_parser.py          # Parsing des données brutes  
│   ├── interface.py            # Interface graphique (Tkinter)  
│   ├── inverted_index.py       # Index inversé pour la recherche  
│   ├── lemmatize.py            # Lemmatisation des termes  
│   ├── segmente.py             # Segmentation du texte  
│   ├── spellchecker.py         # Correction orthographique  
│   ├── substitue.py            # Gestion des synonymes  
│   ├── queries.py              # Traitement des requêtes utilisateur  
│   ├── main.py                 # Script principal pour afficher l'interface  
│   ├── browser.py               # Moteur de recherche principal  
│   ├── eval.py                 # Evaluation du moteur de recherche principal    
│   ├── utils.py                # Fonctions utilitaires  
│   ├── data/                   # Données générées et sources  
│   │   ├── BULLETINS            # Bulletins et images d'origine  
│   │   └── (tous les autres fichiers générés)  
│   └── images/                 # Images pour l’interface  
│       └── icon.png            # Icône de l’interface  
│       └── icon.ico            # Icône de l’interface  

Tous les scripts situés dans le dossier src/ peuvent être exécutés séparément.
Ils fonctionnent chacun de manière autonome, ce qui vous permet de tester et visualiser le traitement étape par étape.
Cela est particulièrement utile si vous souhaitez comprendre ou valider chaque phase du projet avant d’utiliser l’interface graphique.   

Pour générer les fichiers du projet, veuillez suivre les étapes suivantes :
- Etape 1 : lancer data_parser.py
- Etape 2 : lancer segmente.py
- Etape 3 : lancer anti_dictionnary.py
- Etape 4 : lancer lemmatize.py
- Etape 5 : lancer inverted_index.py
---

## Installation

Avant toute chose, il est nécessaire d’installer les dépendances Python listées dans `requirements.txt`.  
Exécutez la commande suivante dans votre terminal :

```bash
pip install -r requirements.txt

```

## Utilisation de l'interface

Pour lancer l’interface graphique, exécutez la commande suivante dans le terminal :

```bash
python src/main.py
```
ou 

```bash
python src/interface.py
```

L’interface, développée avec Tkinter, est intuitive et facile à prendre en main :

- Saisissez votre requête dans la barre de recherche.
- Sélectionnez le mode de tri souhaité parmi les options suivantes :  
  - Tri par pertinence  
  - Tri par date de parution croissante  
  - Tri par date de parution décroissante  
- Cliquez sur **Rechercher** pour afficher les résultats.

**Important :** si vous souhaitez changer le critère de tri, il faut modifier la sélection puis relancer la recherche en cliquant à nouveau sur **Rechercher**.

Les résultats s’affichent sous forme de tableau avec plusieurs colonnes.  
Dans la dernière colonne **Consulter**, un bouton permet d’ouvrir l’article complet directement sur le site de l’ADIT.


### Exemple

Si vous entrez la requête suivante :
```bash
je veux des articles parlant de réalité virtuelle
```
vous obtiendrez la liste des articles correspondants, triés selon votre critère choisi.  
Vous pouvez alors consulter chaque article en cliquant sur le bouton **Consulter**.  

Les temps d’exécution rapportés dans le rapport pour le traitement des requêtes via la fonction moteur.py ont été mesurés sur Google Colab.  
En local, les temps moyens restent relativement similaires.  
Il ne faut pas s’inquiéter si l’exécution est légèrement plus longue de votre côté, cela dépend notamment des performances de votre machine.
