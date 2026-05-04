import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

# Remonter au niveau wsite-section
def get_section(el):
    parent = el
    while parent:
        parent = parent.parent
        if parent and parent.get("class") and "wsite-section" in parent.get("class"):
            return parent
    return None

section_debut = get_section(debut)
section_fin = get_section(fin)

print("=== SECTION DEBUT trouvée:", section_debut is not None)
print("=== SECTION FIN trouvée:", section_fin is not None)

contenu_html = ""
el = section_debut.next_sibling
count = 0
while el and el != section_fin and count < 50:
    contenu_html += str(el)
    el = el.next_sibling
    count += 1

print("=== CONTENU longueur:", len(contenu_html))

data = {
    "titre": "Nouveauté",
    "contenu": contenu_html.strip(),
    "lien_site": url
}

with open("nouveaute.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("OK")
