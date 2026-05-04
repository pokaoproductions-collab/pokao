import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

contenu_html = ""
capture = False
for el in soup.find_all(True):
    if el.get("id") == "nouveaute-debut":
        capture = True
        continue
    if el.get("id") == "nouveaute-fin":
        break
    if capture and not any(p.get("id") in ["nouveaute-debut", "nouveaute-fin"]
                           for p in el.parents):
        contenu_html += str(el)

data = {
    "titre": "Nouveauté",
    "contenu": contenu_html.strip(),
    "lien_site": url
}

with open("nouveaute.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("OK -", len(contenu_html), "caractères extraits")
