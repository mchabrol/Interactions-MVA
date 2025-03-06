# Interactions-MVA

Ce projet est une adaptation de [Pymarket](https://github.com/kenokrieger/pymarket),  
qui implémente le **modèle d’Ising de Bornholdt** en Python.

## 🔹 Modifications et améliorations

Ce projet reprend certaines idées et implémentations de **Pymarket** tout en ajoutant les améliorations suivantes :
- **Refonte en programmation orientée objet (POO)** :  
- **Réorganisation et modularisation du code** pour une meilleure lisibilité.
- **Optimisation des mises à jour des spins** avec une gestion plus efficace des sous-grilles.
- **Ajout de visualisations** pour observer l’évolution du marché en fonction du temps.

L'implémentation originale de **Pymarket** peut être trouvée ici :  
➡️ [Pymarket sur GitHub](https://github.com/kenokrieger/pymarket)

---

## 📂 Notebooks principaux

Quatre notebooks principaux sont inclus dans ce projet, chacun explorant une variation du modèle de base :

- **`main.ipynb`** : Implémente le modèle de base décrit dans le papier et déjà présent dans Pymarket. Il sert de référence pour les autres expériences.
- **`mainwithadvantage.ipynb`** : Introduit une asymétrie d’information en simulant un petit groupe d’agents mieux informés, ce qui permet d’étudier l'impact d’un avantage informationnel sur le marché.
- **`mainwithkrash.ipynb`** : Modélise des krachs boursiers en imposant la vente forcée d’un certain nombre d’agents simultanément, afin d’analyser les dynamiques de panique et d’effondrement du marché.
- **`main_neutral_1.ipynb`** : Explore un modèle où une fraction d’agents adopte une opinion neutre. Ces agents peuvent être distribués aléatoirement ou regroupés dans une zone spécifique (ex: coin supérieur gauche). L’objectif est d’étudier l'impact de ces agents neutres sur les cycles de polarisation et de volatilité du marché.

Chacun de ces notebooks est accompagné d’un fichier `.py` correspondant, qui contient les fonctions implémentant ces expériences.

---

## 📜 **Licence**

L’implémentation originale de **Pymarket** est sous licence MIT.  

