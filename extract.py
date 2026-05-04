import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

# Remonter jusqu'à l'ancêtre commun au niveau le plus haut
def get_top_ancestor(el):
    """Remonte jusqu'au div de niveau page (enfant direct de wsite-content)"""
    wsite = soup.find(class_="wsite-content")
    if not wsite:
        wsite = soup.body
    parent = el
    while parent.parent and parent.parent != wsite:
        parent = parent.parent
    return parent

top_debut = get_top_ancestor(debut)
top_fin = get_top_ancestor(fin)

print("=== TOP DEBUT:", str(top_debut)[:200])
print("=== TOP FIN:", str(top_fin)[:200])

# Collecter tout ce qui est entre les deux
contenu_html = ""
el = top_debut.next_sibling
count = 0
while el and el != top_fin and count < 50:
    contenu_html += str(el)
    el = el.next_sibling
    count += 1

print("=== CONTENU longueur:", len(contenu_html))
print("=== CONTENU debut:", contenu_html[:500])

data = {
    "titre": "Nouveauté",
    "contenu": contenu_html.strip(),
    "lien_site": url
}

with open("nouveaute.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("OK")
