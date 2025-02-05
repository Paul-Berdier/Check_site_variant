# Analyse et Détection de Sites de Phishing

## Description
Ce projet permet d'identifier des sites frauduleux similaires à un site officiel donné et d'analyser les informations IP des sites détectés. Il s'appuie sur les outils **dnstwist**, **BeautifulSoup**, **FuzzyWuzzy**, et l'API **ipinfo.io**.

## Fonctionnalités
1. **Détection de sites de phishing** :
   - Génération de variantes de domaines via **dnstwist**.
   - Vérification de l'existence et de l'accessibilité des domaines générés.
   - Scraping de la structure HTML des sites trouvés.
   - Comparaison avec la structure HTML du site officiel et de ses variantes.
   - Stockage des sites frauduleux détectés dans `sites_frauduleux.txt`.

2. **Analyse des IP des sites frauduleux** :
   - Lecture des domaines stockés dans `sites_frauduleux.txt`.
   - Récupération des informations des IP via **ipinfo.io**.
   - Génération d'un rapport détaillé dans `sites_frauduleux_ipinfo.txt`.

## Installation
### Prérequis
- **Python 3.x**
- **pip** (gestionnaire de paquets Python)

### Installation des dépendances
Exécute la commande suivante pour installer toutes les bibliothèques requises :
```sh
pip install -r requirements.txt
```

### Configuration
Créer un fichier `.env` à la racine du projet contenant :
```
SITE_OFFICIEL=exemple.com
EXEMPLES_COPIE=exemple.com,exemple2.com
VARIANTS_SITE_OFFICIEL=exemple,exemple2,exemple3    #sans le .com
IPINFO_API_KEY=YOUR_IPINFO_API_KEY
```
- Remplace `YOUR_IPINFO_API_KEY` par ta clé API ipinfo.io.
- Les `VARIANTS_SITE_OFFICIEL` ne doit pas avoir de .xxx

## Utilisation
Lancer le script principal :
```sh
python main.py
```
Une question te sera posée :
- **1** : Recherche des sites frauduleux similaires au site officiel.
- **2** : Analyse des IP des sites frauduleux listés dans `sites_frauduleux.txt`.

## Fichiers Importants
- **`main.py`** : Point d'entrée du script.
- **`fishing_sites_script.py`** : Recherche et analyse des sites de phishing.
- **`analyse_ipinfo.py`** : Analyse des IP des sites frauduleux.
- **`sites_frauduleux.txt`** : Liste des sites frauduleux détectés.
- **`sites_frauduleux_ipinfo.txt`** : Détails des IP et hébergeurs des sites frauduleux.

## Améliorations Futures
- Ajout d'une interface graphique.
- Intégration d'autres bases de données pour vérifier les sites suspects.
- Envoi de rapports automatiques par email.

## Auteurs
- **Paul Berdier**

