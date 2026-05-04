import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
base_url = "https://bakasabl.weebly.com"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

parent_debut = debut.find_parent("div", class_="wcustomhtml").parent
parent_fin = fin.find_parent("div", class_="wcustomhtml").parent

contenu_html = ""
el = parent_debut.next_sibling
while el:
    if el == parent_fin:
        break
    if hasattr(el, 'find_all') and el.find(id="nouveaute-fin"):
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
