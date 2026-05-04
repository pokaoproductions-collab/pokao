import requests
from bs4 import BeautifulSoup
import json

url = "https://bakasabl.weebly.com/ess.html"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(r.text, "html.parser")

# Cherche les balises de toutes les façons possibles
debut = soup.find(id="nouveaute-debut")
fin = soup.find(id="nouveaute-fin")

print("=== DEBUT trouvé:", debut)
print("=== FIN trouvée:", fin)

# Affiche toute la zone centrale de la page
wsite = soup.find(class_="wsite-content")
if wsite:
    print("=== WSITE CONTENT:")
    print(wsite.prettify()[:3000])
else:
    print("=== PAS DE WSITE-CONTENT, voici le body:")
    print(soup.body.prettify()[:3000])

data = {"titre": "Nouveauté", "contenu": "", "lien_site": url}
with open("nouveaute.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
