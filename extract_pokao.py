import requests
from bs4 import BeautifulSoup, Comment
import json

url = "https://pokao.weebly.com/anim-animaux.html"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

# Chercher le commentaire <!-- NOUVEAUTE -->
comments = soup.find_all(string=lambda t: isinstance(t, Comment))
marker = None
for c in comments:
    if c.strip() == "NOUVEAUTE":
        marker = c
        break

if not marker:
    print("Commentaire <!-- NOUVEAUTE --> non trouvé")
    exit(1)

# La section est le nœud suivant du commentaire
section = marker.find_next_sibling()
if not section:
    print("Aucun élément après <!-- NOUVEAUTE -->")
    exit(1)

# Extraire titre, texte, src iframe
title_tag = section.find(class_="nse-title")
text_tag  = section.find(class_="nse-text")
iframe    = section.find("iframe", class_="nse-anim")

titre = title_tag.get_text(strip=True) if title_tag else ""
texte = text_tag.get_text(" ", strip=True) if text_tag else ""
lien  = iframe["src"] if iframe and iframe.get("src") else ""

print("=== TITRE:", titre)
print("=== TEXTE:", texte[:100])
print("=== LIEN:",  lien)

if not titre and not lien:
    print("Données vides — vérifier la structure HTML")
    exit(1)

data = {
    "titre": titre,
    "texte": texte,
    "lien":  lien,
    "lien_site": url
}

with open("nouveaute_pokao.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("OK")
