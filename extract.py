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

# Parcourir tous les éléments directs de wsite-section-elements
elements = section.find("div", class_="wsite-section-elements")
if not elements:
    elements = section

capture = False
contenu_html = ""

for child in elements.children:
    if not hasattr(child, 'find'):
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
