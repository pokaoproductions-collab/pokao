import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
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

section_debut = get_section(debut)
section_fin = get_section(fin)

# Afficher les siblings pour comprendre la structure
print("=== SIBLINGS entre debut et fin:")
el = section_debut.next_sibling
count = 0
while el and el != section_fin and count < 20:
    print(f"  sibling {count}: type={type(el).__name__} contenu={str(el)[:100]}")
    el = el.next_sibling
    count += 1

data = {"titre": "Nouveauté", "contenu": "", "lien_site": url}
with open("nouveaute.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("OK")
