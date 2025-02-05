import requests
import os
import time
from dotenv import load_dotenv

def analyser_sites_frauduleux():
    """
    Analyse les sites frauduleux depuis 'sites_frauduleux.txt' en récupérant leurs IP et informations via IPinfo.
    Les résultats sont enregistrés dans 'details_sites_frauduleux.txt'.
    """
    # Charger les variables d'environnement
    load_dotenv()
    IPINFO_TOKEN = os.getenv("IPINFO_TOKEN")

    if not IPINFO_TOKEN:
        print("🚨 ERREUR : Clé API IPinfo non trouvée. Vérifie ton fichier .env !")
        return

    # 📂 Lire le fichier des sites frauduleux
    fraudulent_sites = []
    try:
        with open("sites_frauduleux.txt", "r") as file:
            for line in file:
                parts = line.strip().split(" - ")
                if len(parts) >= 2:
                    site, score = parts[:2]  # Prendre au moins site et score
                    ip = parts[2].replace("IP: ", "") if len(parts) > 2 else "N/A"
                    fraudulent_sites.append((site, score, ip))
    except FileNotFoundError:
        print("🚨 ERREUR : Le fichier 'sites_frauduleux.txt' est introuvable.")
        return

    # 🔍 Fonction pour récupérer les infos IP
    def get_ip_info(ip):
        if ip == "N/A":
            return None  # Pas d'IP connue pour ce site
        url = f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()

            if "bogon" in data:
                return None  # Adresse IP non routable

            return {
                "ip": data.get("ip", "N/A"),
                "hostname": data.get("hostname", "N/A"),
                "city": data.get("city", "N/A"),
                "region": data.get("region", "N/A"),
                "country": data.get("country", "N/A"),
                "org": data.get("org", "N/A"),
                "asn": data.get("asn", {}).get("asn", "N/A"),
            }
        except requests.RequestException:
            return None

    # 📍 Récupérer les infos IP pour chaque site frauduleux
    details = []
    for site, score, ip in fraudulent_sites:
        print(f"🔎 Recherche des infos pour {site} (IP: {ip})...")
        ip_info = get_ip_info(ip)

        if ip_info:
            details.append(
                f"{site} - {score} - IP: {ip_info['ip']} - {ip_info['city']}, {ip_info['region']}, {ip_info['country']} - "
                f"{ip_info['org']} - ASN: {ip_info['asn']}"
            )
        else:
            details.append(f"{site} - {score} - IP: {ip} - ❌ Infos non disponibles")

        time.sleep(1)  # 🕒 Éviter de surcharger l'API

    # 📄 Enregistrer les résultats
    with open("details_sites_frauduleux.txt", "w") as file:
        for entry in details:
            file.write(entry + "\n")

    print("\n✅ Analyse terminée ! Les résultats sont enregistrés dans 'details_sites_frauduleux.txt'.")

# 📌 Exécuter l'analyse
if __name__ == "__main__":
    analyser_sites_frauduleux()
