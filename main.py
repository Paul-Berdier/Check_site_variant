#!/usr/bin/env python3
import os
import json
import subprocess
from dotenv import load_dotenv
import sys

# Charger les variables d'environnement depuis .env
load_dotenv()

# Récupérer la liste des domaines à surveiller
LIST_DOMAINES = os.getenv('LIST_DOMAINES')

# Fichier de sortie
OUTPUT_FILE = "resultats_dnstwist.txt"

if not LIST_DOMAINES:
    print("⚠️ Aucune liste de domaines définie dans .env (LIST_DOMAINES)")
    exit(1)


def run_dnstwist(domain):
    """
    Exécute dnstwist sur un domaine donné et retourne la sortie texte.
    """
    try:
        command = [
            sys.executable, "-m", "dnstwist",
            "--registered",
            domain
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return result.stdout  # Retourner la sortie brute en texte
        else:
            print(f"❌ Erreur lors de l'exécution de dnstwist pour {domain}: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return None


def main():
    """
    Traite chaque domaine de la liste, affiche et enregistre les résultats.
    """
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("📌 Résultats d'analyse dnstwist\n\n")

        for original_domain in LIST_DOMAINES.split(','):
            original_domain = original_domain.strip()  # Nettoyer les espaces éventuels
            print(f"\n🔎 Analyse de : {original_domain}")

            results = run_dnstwist(original_domain)

            if results:
                print(f"✅ Résultats enregistrés pour {original_domain}")
                file.write(f"\n🔎 Domaine analysé : {original_domain}\n")
                file.write(results)  # Sauvegarder la sortie brute de dnstwist
                file.write("\n" + "=" * 50 + "\n")  # Séparateur
            else:
                print(f"⚠️ Aucun résultat pour {original_domain}")
                file.write(f"\n🔎 Domaine analysé : {original_domain}\n⚠️ Aucun résultat.\n")
                file.write("\n" + "=" * 50 + "\n")  # Séparateur

    print(f"\n📂 Tous les résultats ont été enregistrés dans '{OUTPUT_FILE}'")


if __name__ == "__main__":
    main()
