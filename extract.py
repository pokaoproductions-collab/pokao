import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
base_url = "https://bakasabl.weebly.com"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

# Remonter 3 niveaux au lieu de 2
def get_bloc(el):
    p = el.find_parent("div", class_="wcustomhtml")
    return p.parent.parent if p else None

bloc_debut = get_bloc(debut)
bloc_fin = get_bloc(fin)

print("=== bloc_debut class:", bloc_debut.get("class") if bloc_debut else "None")
print("=== bloc_fin class:", bloc_fin.get("class") if bloc_fin else "None")
print("=== meme element?", bloc_debut == bloc_fin)

contenu_html = ""
el = bloc_debut.next_sibling
while el:
    if el == bloc_fin:
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
