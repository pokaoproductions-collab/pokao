import requests
import re
import json

url = "https://pokao.weebly.com/anim-animaux.html"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

# Extraire le bloc NSE_SCENES du JavaScript
match = re.search(r'window\.NSE_SCENES\s*=\s*(\[.*?\]);', r.text, re.DOTALL)
if not match:
    print("NSE_SCENES non trouvé")
    exit(1)

scenes_raw = match.group(1)

# Chercher l'élément avec nouveaute: true
match_scene = re.search(
    r'\{[^}]*"nouveaute"\s*:\s*true[^}]*\}',
    scenes_raw,
    re.DOTALL
)
if not match_scene:
    print("Aucune scène avec nouveaute: true")
    exit(1)

scene_raw = match_scene.group(0)

# Extraire title, text, src
title = re.search(r'"title"\s*:\s*"(.*?)"', scene_raw)
text = re.search(r'"text"\s*:\s*"(.*?)"', scene_raw, re.DOTALL)
src = re.search(r'"src"\s*:\s*"(.*?)"', scene_raw)

data = {
    "titre": title.group(1) if title else "",
    "texte": text.group(1).strip() if text else "",
    "lien": src.group(1) if src else "",
    "lien_site": url
}

print("=== TITRE:", data["titre"])
print("=== TEXTE:", data["texte"][:100])
print("=== LIEN:", data["lien"])

with open("nouveaute_pokao.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("OK")
