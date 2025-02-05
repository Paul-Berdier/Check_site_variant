import requests
import time
import socket
import subprocess
import logging
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Configuration des logs
logging.basicConfig(
    filename='resultats.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Extensions de domaine à tester
extensions_sup = [
    ".com", ".net", ".org", ".info", ".biz", ".us", ".eu", ".fr", ".de", ".it",
    ".es", ".jp", ".uk", ".nl", ".ch", ".be", ".ca", ".ru", ".mx", ".br", ".in",
    ".kr", ".se", ".no", ".fi", ".dk", ".gr", ".pt", ".pl", ".cz", ".sk", ".tr"
]

# Vrai site à comparer
SITE_OFFICIEL = os.getenv("SITE_OFFICIEL")
EXEMPLES_COPIE = os.getenv("EXEMPLES_COPIE")
VARIANTS = os.getenv("VARIANTS_SITE_OFFICIEL")


# Vérifier si VARIANTS est défini et non vide
if VARIANTS:
    domaines_base = VARIANTS.split(",")  # Convertir la chaîne en liste
else:
    domaines_base = []  # Liste vide si aucune variante définie

# Vérifier si VARIANTS est défini et non vide
if EXEMPLES_COPIE:
    ex_copie = EXEMPLES_COPIE.split(",")  # Convertir la chaîne en liste
else:
    ex_copie = []  # Liste vide si aucune variante définie

# Ajouter le vrai site à la liste s'il est défini
if SITE_OFFICIEL:
    domaines_base.append(SITE_OFFICIEL.split(".")[0])


# ✅ Fonction pour scraper une page web et extraire sa structure HTML
def scrape_structure(url):
    """Scrape la structure HTML et extrait les balises importantes pour comparaison."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")

        elements = []

        # 🔹 Ajout de balises supplémentaires pour capter plus d'infos
        for tag in soup.find_all(["input", "button", "form", "a", "select", "textarea", "div", "span", "nav", "section"]):
            tag_info = {
                "tag": tag.name,
                "attributes": tag.attrs  # Récupère tous les attributs
            }
            elements.append(tag_info)

        # 🔍 Si aucune balise trouvée, afficher un extrait du HTML (debug)
        if not elements:
            print(f"⚠️ Aucune balise trouvée sur {url}. Voici un extrait du HTML récupéré :")
            print(soup.prettify()[:1000])  # Affiche les 1000 premiers caractères du HTML pour voir ce qui est récupéré.

        return elements

    except requests.exceptions.RequestException:
        return None


def domaine_existe(domaine):
    """Vérifie si un domaine a un enregistrement DNS valide."""
    try:
        socket.gethostbyname(domaine)
        return True
    except socket.gaierror:
        return False

def tester_url(domaine):
    """Teste l'accessibilité du domaine et retourne son texte."""
    urls = [f"http://{domaine}", f"https://{domaine}"]

    for url in urls:
        try:
            start_time = time.time()
            response = requests.get(url, headers=HEADERS, timeout=5)
            end_time = time.time()
            duration = end_time - start_time

            if response.status_code == 200:
                print(f"[SUCCESS] {url} est accessible en {duration:.2f} sec.")
                logging.info(f"[SUCCESS] {url} est accessible.")
                return url, scrape_structure(url)
        except requests.RequestException:
            pass  # Ignorer les erreurs de connexion

    return None, ""

def generer_variantes_dnstwist(domaines):
    """Génère des variantes de domaine en utilisant dnstwist."""
    variantes = set()

    for domaine in domaines:
        print(f"🔍 Génération des variantes pour {domaine} via dnstwist...")
        try:
            result = subprocess.run(
                ["dnstwist", "--all", "--registered", domaine],
                capture_output=True, text=True, check=True
            )

            for line in result.stdout.split("\n"):
                parts = line.split()
                if len(parts) > 1 and parts[0] != "*original":
                    variantes.add(parts[1])

        except subprocess.CalledProcessError:
            print(f"⚠️ Erreur avec dnstwist pour {domaine}")

    return list(variantes)

def comparer_sites(sites_trouves, seuil_pourcent=30):
    """Compare les structures HTML des sites suspects avec celles du site officiel et garde ceux avec une similarité >30%."""
    print("\n🔍 Comparaison de la structure HTML avec le site officiel et ses variantes...")

    # Récupérer la structure HTML de toutes les variantes officielles
    structures_officielles = {}
    urls_officielles = ex_copie + [SITE_OFFICIEL]  # ✅ Bonne concaténation

    for url in urls_officielles:
        if url:
            print(f"🔎 Scraping de {url}...")
            structure = scrape_structure(f"https://{url.strip()}")
            if structure:
                structures_officielles[url] = structure

    if not structures_officielles:
        print("🚨 ERREUR : Impossible de récupérer la structure HTML du site officiel et ses variantes.")
        return []

    # Convertir les structures officielles en texte pour la comparaison
    structures_officielles_txt = {
        url: " ".join([f"{e['tag']}:{str(e['attributes'])}" for e in structure])
        for url, structure in structures_officielles.items()
    }

    sites_frauduleux = []

    for url_suspect, structure_suspecte in sites_trouves.items():
        if not structure_suspecte:
            continue  # Ignorer les sites sans structure HTML

        # Convertir la structure suspecte en texte
        structure_suspecte_txt = " ".join([f"{e['tag']}:{str(e['attributes'])}" for e in structure_suspecte])

        # 📊 Comparer avec toutes les variantes et garder l'URL officielle avec le score le plus élevé
        meilleur_score = 0
        meilleure_variation = ""

        for url_off, structure_txt in structures_officielles_txt.items():
            score = fuzz.token_sort_ratio(structure_txt, structure_suspecte_txt)
            if score > meilleur_score:
                meilleur_score = score
                meilleure_variation = url_off

        print(f"📊 Similarité avec {url_suspect} (meilleur match : {meilleure_variation}) : {meilleur_score}%")

        # Si la similarité est supérieure au seuil, on garde ce site suspect pour la prochaine boucle
        if meilleur_score >= seuil_pourcent:
            sites_frauduleux.append((url_suspect, meilleur_score))

    # 🔽 Trier par similarité décroissante et stocker dans un fichier
    sites_frauduleux.sort(key=lambda x: x[1], reverse=True)

    with open("sites_frauduleux.txt", "w") as f:
        for site, score in sites_frauduleux:
            f.write(f"{site} - {score}%\n")

    print(f"✅ {len(sites_frauduleux)} sites frauduleux enregistrés dans sites_frauduleux.txt.")

    # Ne renvoyer que les domaines suspects qui ont dépassé le seuil
    return [site[0].replace("http://", "").replace("https://", "") for site in sites_frauduleux]

def explorer_domaines(domaines):
    """Teste les domaines et les variantes de manière itérative jusqu'à épuisement."""
    nouveaux_domaines = {f"{d}{ext}" for d in domaines for ext in extensions_sup}
    domaines_testes = set()
    sites_trouves = {}

    while nouveaux_domaines:
        print(f"\n🔄 Itération avec {len(nouveaux_domaines)} domaines à tester...")

        # Tester les nouveaux domaines et stocker ceux qui répondent
        for domaine in nouveaux_domaines:
            url, texte = tester_url(domaine)
            if url:
                sites_trouves[url] = texte  # Stocke l'URL et le texte du site

        if not sites_trouves:
            print("✅ Plus de nouveaux domaines trouvés. Fin de l'exploration.")
            break

        print(f"✅ {len(sites_trouves)} nouveaux domaines accessibles trouvés !")

        # Comparer avec le site officiel et ne garder que ceux qui ont > 10% de ressemblance
        domaines_similaires = comparer_sites(sites_trouves)

        if not domaines_similaires:
            print("🚫 Aucun site ne dépasse 10% de similarité. Arrêt de l'exploration.")
            break

        # Générer de nouvelles variantes basées sur les domaines similaires
        nouveaux_domaines = set(generer_variantes_dnstwist(domaines_similaires))

        # Filtrer pour ne pas retester ceux déjà vus
        nouveaux_domaines -= domaines_testes
        domaines_testes.update(nouveaux_domaines)

    return domaines_testes

# Lancer l'exploration et comparer avec le vrai site
sites_trouves = explorer_domaines(domaines_base)
print(f"\n🎯 Exploration terminée. Total de {len(sites_trouves)} sites trouvés et comparés.")
