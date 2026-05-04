import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
base_url = "https://bakasabl.weebly.com"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

# Remonter jusqu'à wsite-section pour chacun
def get_section(el):
    parent = el
    while parent:
        parent = parent.parent
        if parent and parent.get("class") and "wsite-section" in parent.get("class"):
            return parent
    return None

section_debut = get_section(debut)
section_fin = get_section(fin)

print("=== section_debut class:", section_debut.get("class") if section_debut else "None")
print("=== section_fin class:", section_fin.get("class") if section_fin else "None")
print("=== meme element?", section_debut == section_fin)

contenu_html = ""
el = section_debut.next_sibling
while el:
    if el == section_fin:
        break
    contenu_html += str(el)
    el = el.next_sibling

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
