import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
base_url = "https://bakasabl.weebly.com"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

def get_section(el):
    parent = el
    while parent:
        parent = parent.parent
        if parent and parent.get("class") and "wsite-section" in parent.get("class"):
            return parent
    return None

section = get_section(debut)
elements = section.find("div", class_="wsite-section-elements") or section

# L'enfant 7 contient tout — on le trouve comme le div qui contient nouveaute-fin
conteneur = None
for child in elements.children:
    if hasattr(child, 'find_all') and child.find(id="nouveaute-fin"):
        conteneur = child
        break

print("=== CONTENEUR trouvé:", conteneur is not None)

# Extraire les wcustomhtml entre debut et fin dans ce conteneur
capture = False
contenu_html = ""
for child in conteneur.children:
    if not hasattr(child, 'find_all'):
        continue
    if child.find(id="nouveaute-debut"):
        capture = True
        continue
    if child.find(id="nouveaute-fin"):
        break
    if capture:
        contenu_html += str(child)

contenu_html = contenu_html.replace('src="/uploads/', f'src="{base_url}/uploads/')
print("=== CONTENU longueur:", len(contenu_html))

data = {
    "titre": "Nouveauté",
    "contenu": contenu_html.strip(),
    "lien_site": url
}

with open("nouveaute.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("OK")
