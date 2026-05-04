import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
base_url = "https://bakasabl.weebly.com"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

# Remonter au div wcustomhtml parent
parent_debut = debut.find_parent("div", class_="wcustomhtml")
parent_fin = fin.find_parent("div", class_="wcustomhtml")

# Remonter encore un niveau (le div englobant)
bloc_debut = parent_debut.parent
bloc_fin = parent_fin.parent

# Collecter tout ce qui est entre les deux blocs
contenu_html = ""
el = bloc_debut.next_sibling
while el and el != bloc_fin:
    contenu_html += str(el)
    el = el.next_sibling

# Corriger les chemins d'images relatifs
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
