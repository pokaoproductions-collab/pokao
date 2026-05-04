import requests
from bs4 import BeautifulSoup
import json
import re

url = "https://bakasabl.weebly.com/ess.html"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

contenu_html = ""
if debut and fin:
    el = debut.next_sibling
    while el and el != fin:
        contenu_html += str(el)
        el = el.next_sibling

data = {
    "titre": "Nouveauté",
    "contenu": contenu_html.strip(),
    "lien_site": url
}

with open("nouveaute.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("OK")
