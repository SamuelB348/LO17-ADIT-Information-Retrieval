# LO17-ADIT-Information-Retrieval

## Description

Ce projet est un moteur de recherche d’informations sur une archive de l'ADIT, développé dans le cadre du cours LO17 à l'UTC.  
Il permet d’indexer, traiter et rechercher des articles à partir d’un corpus de bulletins, avec une interface graphique intuitive.

---

## Organisation du projet

À la racine du projet, on trouve :

- `BULLETINS.zip` : archive contenant les données initiales (bulletins et images associées).
- `.gitignore` : fichier pour exclure certains fichiers du suivi Git.
- `requirements.txt` : liste des dépendances Python nécessaires au projet.
- `Rapport_Projet_LO17.pdf` : rapport de projet résumant tous les TDs.  
- `src/` : dossier principal contenant tous les scripts Python, organisés pour faciliter le développement et les tests.

Dans le dossier src, on trouve :
- `images/` : contient les icônes utilisées pour l’interface graphique.
- `data/` : contient tous les fichiers générés lors de l’exécution du projet ainsi que le dossier `BULLETINS/` avec les bulletins et images sources.
- les fichiers python du projet

---

### Structure détaillée du projet

/ (racine)  
├── BULLETINS.zip          # Archive contenant les bulletins initiaux  
├── .gitignore             # Fichier Git pour ignorer certains fichiers  
├── requirements.txt       # Liste des dépendances Python  
├── README.md              # Ce fichier readme  
├── src/                   # Dossier principal des scripts et ressources  
│   ├── anti_dictionnaire.py     # Filtrage des mots vides  
│   ├── traitement_donnees.py          # Parsing des données brutes  
│   ├── interface.py            # Interface graphique (Tkinter)  
│   ├── index_inverse.py       # Index inversé pour la recherche  
│   ├── lemmatisation.py            # Lemmatisation des termes  
│   ├── segmente.py             # Segmentation du texte  
│   ├── correcteur.py         # Correction orthographique  
│   ├── substitue.py            # Gestion des synonymes  
│   ├── requetes.py              # Traitement des requêtes utilisateur  
│   ├── main.py                 # Script principal pour afficher l'interface  
│   ├── moteur.py              # Moteur de recherche principal  
│   ├── evaluation.py                 # Evaluation du moteur de recherche principal    
│   ├── utils.py                # Fonctions utilitaires  
│   ├── data/                   # Données générées et sources  
│   │   ├── BULLETINS/          # Bulletins et images d'origine  
│   │   └── (tous les autres fichiers générés)  
│   ├── images/                 # Images pour l’interface  
│       ├── icon.ico            # Icône de l’interface  
│       ├── icon.png            # Icône de l’interface  

Tous les scripts situés dans le dossier src/ peuvent être exécutés séparément.
Ils fonctionnent chacun de manière autonome, ce qui vous permet de tester et visualiser le traitement étape par étape.
Cela est particulièrement utile si vous souhaitez comprendre ou valider chaque phase du projet avant d’utiliser l’interface graphique.   

Pour générer les fichiers du projet, veuillez suivre les étapes suivantes :
- Etape 1 : lancer traitement_donnees.py
- Etape 2 : lancer segmente.py
- Etape 3 : lancer anti_dictionnaire.py
- Etape 4 : lancer lemmatisation.py
- Etape 5 : lancer index_inverse.py
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

L’interface, développée avec Tkinter, est intuitive et facile à prendre en main :

- Saisissez votre requête dans la barre de recherche.
- Sélectionnez le mode de tri souhaité parmi les options suivantes :  
  - Tri dit 'classique' : pas de tri (option par défaut) 
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


### Évaluation du code

Enfin, pour assurer un code propre, lisible et conforme aux bonnes pratiques, nous avons utilisé l’outil `pylint` afin d’analyser l’ensemble de notre base de code. Grâce à ce travail, nous avons obtenu un score global supérieur à **9.92 / 10**, ce qui témoigne d’un code bien structuré, bien documenté et maintenable.

La commande utilisée pour obtenir ce score est la suivante :

```bash
pylint --disable=C0301 src/*.py
```

