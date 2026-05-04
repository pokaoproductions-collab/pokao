import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

# Afficher toute la chaîne de parents de debut
print("=== PARENTS DE DEBUT:")
el = debut
for i in range(10):
    el = el.parent
    if el is None:
        break
    print(f"  niveau {i+1}: tag={el.name} class={el.get('class')} id={el.get('id')}")

data = {"titre": "Nouveauté", "contenu": "", "lien_site": url}
with open("nouveaute.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("OK")
