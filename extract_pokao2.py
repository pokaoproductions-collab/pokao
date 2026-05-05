import requests
from bs4 import BeautifulSoup
import json

with open("config_pokao2.json", "r") as f:
    config = json.load(f)

url = config["url"]
base_url = "https://pokao.weebly.com"
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

section = get_section(fin)
elements = section.find("div", class_="wsite-section-elements") or section

# Trouver les blocs conteneurs de debut et fin
bloc_debut = None
bloc_fin = None
for child in elements.children:
    if hasattr(child, 'find_all'):
        if child.find(id="nouveaute-debut"):
            bloc_debut = child
        if child.find(id="nouveaute-fin"):
            bloc_fin = child

print("=== bloc_debut trouvé:", bloc_debut is not None)
print("=== bloc_fin trouvé:", bloc_fin is not None)

# Collecter tout ce qui est entre les deux blocs
contenu_html = ""
if bloc_debut and bloc_fin:
    el = bloc_debut.next_sibling
    while el and el != bloc_fin:
        contenu_html += str(el)
        el = el.next_sibling

contenu_html = contenu_html.replace('src="/uploads/', f'src="{base_url}/uploads/')
print("=== CONTENU longueur:", len(contenu_html))

data = {
    "titre": "Nouveauté",
    "contenu": contenu_html.strip(),
    "lien_site": url
}

with open("nouveaute_pokao2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("OK")
