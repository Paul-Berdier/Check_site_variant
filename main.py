from fishing_sites_script import *
from analyse_ipinfo import *

def main():
    mode = input("Voulez-vous chercher des nom de sites de fishing pa rapport à un site (1) sinon avoir les informations des IP de sites (2) ?")
    if mode == "1":
         # Lancer l'exploration et comparer avec le vrai site
        sites_trouves = explorer_domaines(domaines_base)
        print(f"\n🎯 Exploration terminée. Total de {len(sites_trouves)} sites trouvés et comparés.")
    elif mode == "2":
        analyser_sites_frauduleux()
    else:
        print("Choix invalide. Veuillez entrer 1 ou 2.")


if __name__ == "__main__":
    main()
