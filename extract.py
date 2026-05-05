import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
base_url = "https://bakasabl.weebly.com"
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

section = get_section(debut)
elements = section.find("div", class_="wsite-section-elements") or section

conteneur = None
for child in elements.children:
    if hasattr(child, 'find_all') and child.find(id="nouveaute-fin"):
        conteneur = child
        break

# Afficher les enfants directs du conteneur
print("=== ENFANTS DU CONTENEUR:")
for i, child in enumerate(conteneur.children):
    if hasattr(child, 'get'):
        has_debut = bool(child.find(id="nouveaute-debut")) if hasattr(child, 'find') else False
        has_fin = bool(child.find(id="nouveaute-fin")) if hasattr(child, 'find') else False
        print(f"  {i}: class={child.get('class')} debut={has_debut} fin={has_fin} contenu={str(child)[:80]}")
    else:
        print(f"  {i}: texte")

data = {"titre": "Nouveauté", "contenu": "", "lien_site": url}
with open("nouveaute.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("OK")
