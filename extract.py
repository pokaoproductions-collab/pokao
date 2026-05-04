import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
base_url = "https://bakasabl.weebly.com"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

# Remonter au div englobant (2 niveaux au dessus de wcustomhtml)
def get_bloc(el):
    p = el.find_parent("div", class_="wcustomhtml")
    return p.parent if p else None

bloc_debut = get_bloc(debut)
bloc_fin = get_bloc(fin)

print("=== bloc_debut id:", bloc_debut.get("id") if bloc_debut else "None")
print("=== bloc_fin id:", bloc_fin.get("id") if bloc_fin else "None")
print("=== meme element?", bloc_debut == bloc_fin)

# Lister tous les siblings
el = bloc_debut.next_sibling
count = 0
while el and count < 20:
    tag = el.name if hasattr(el, 'name') else "texte"
    ids = el.get("id") if hasattr(el, 'get') else ""
    print(f"  sibling {count}: {tag} id={ids} == fin? {el == bloc_fin}")
    if el == bloc_fin:
        break
    el = el.next_sibling
    count += 1

data = {"titre": "Nouveauté", "contenu": "", "lien_site": url}
with open("nouveaute.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("OK")
