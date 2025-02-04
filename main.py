#!/usr/bin/env python3
import dns.resolver


# -- Partie 1 : Génération de variantes --
def generate_domain_variants(domain):
    """
    Génère des noms de domaines ressemblants par quelques opérations simples :
      - Retrait d'une lettre
      - Substitution d'une lettre par une voisine (simple exemple)
      - Ajout d'une lettre (exemple simple)
    Cette fonction peut être étendue suivant vos besoins.
    """
    variants = set()

    # On sépare le nom de domaine et son TLD (ex: "exemple" et "com" si domaine = "exemple.com")
    if '.' in domain:
        name_part, tld_part = domain.rsplit('.', 1)
    else:
        # Si pas de point, on ne fait pas de split TLD
        name_part = domain
        tld_part = ""

    # Liste de lettres voisines simple (clavier AZERTY par exemple)
    voisins = {
        'a': 'zq', 'z': 'as', 'e': 'zr', 'r': 'et', 't': 'ry',
        'y': 'tu', 'u': 'yi', 'i': 'uo', 'o': 'ip', 'p': 'o',
        # ... adapter selon vos besoins
    }

    # 1) Retrait d'une lettre
    for i in range(len(name_part)):
        # On retire la lettre i
        variant = name_part[:i] + name_part[i + 1:]
        if tld_part:
            variant = variant + '.' + tld_part
        variants.add(variant)

    # 2) Substitution par une lettre voisine
    for i in range(len(name_part)):
        original_letter = name_part[i]
        if original_letter in voisins:
            for neighbor in voisins[original_letter]:
                variant = name_part[:i] + neighbor + name_part[i + 1:]
                if tld_part:
                    variant += '.' + tld_part
                variants.add(variant)

    # 3) Ajout d'une lettre (simplement 'a' à 'z' par exemple)
    import string
    for i in range(len(name_part) + 1):
        for c in string.ascii_lowercase:
            variant = name_part[:i] + c + name_part[i:]
            if tld_part:
                variant += '.' + tld_part
            variants.add(variant)

    # 4) On peut imaginer varier aussi le TLD (ex: .fr, .net, .co, etc.)
    #    Ici, on met simplement un exemple avec 2-3 TLDs
    tlds_test = ['fr', 'net', 'co', 'org']
    if tld_part:
        for new_tld in tlds_test:
            variants.add(name_part + '.' + new_tld)

    return variants


# -- Partie 2 : Vérification DNS --
def check_domain_registered(domain):
    """
    Retourne True si le domaine existe réellement (réponse DNS),
    False sinon.
    """
    try:
        # On essaie de résoudre l'enregistrement A
        answers = dns.resolver.resolve(domain, 'A')
        if answers:
            return True
        else:
            return False
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.LifetimeTimeout):
        return False
    except Exception as e:
        # En cas d'erreur inattendue
        print(f"Erreur DNS sur {domain}: {e}")
        return False


def main():
    # Nom de domaine à surveiller
    original_domain = "exemple.com"

    print(f"[+] Génération de variantes pour : {original_domain}")
    variants = generate_domain_variants(original_domain)

    print(f"[+] Nombre de variantes générées : {len(variants)}")

    # Filtrer éventuellement pour éviter de re-tester le domaine d'origine
    variants.discard(original_domain)

    print("[+] Vérification DNS pour chaque variante...\n")
    found_domains = []

    for dom in variants:
        if check_domain_registered(dom):
            found_domains.append(dom)

    if found_domains:
        print("[!] Domaines existants détectés :")
        for d in found_domains:
            print("    -", d)
    else:
        print("[+] Aucun domaine existant similaire n'a été détecté (dans cette liste de variantes).")


if __name__ == "__main__":
    main()
