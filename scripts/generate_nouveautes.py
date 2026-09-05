#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robot des nouveautés POKAO — v2, sans dépôt du site sur GitHub
================================================================

Contrairement à moulinette-nouveautes.html (saisie manuelle du titre,
de l'image et du texte) et contrairement à la première version de ce
robot (qui exigeait de déposer tout le site sur GitHub), cette version
fonctionne exactement comme l'ancien scraper Weebly : elle va chercher
les informations directement sur le site EN LIGNE, via des requêtes
HTTP. Votre méthode de déploiement (zip envoyé à la main sur le
tableau de bord Cloudflare) ne change pas.

Ce que fait ce script, sans aucune saisie manuelle :

1. Télécharge https://pokao.pages.dev/sitemap.xml (régénéré par vous
   avec scripts/generer_sitemap.py avant chaque déploiement).
2. Compare la liste des pages à `data/nouveautes-manifest.json`
   (mémoire des pages déjà connues) pour repérer les pages NOUVELLES.
3. Pour chaque nouvelle page, télécharge son HTML et en extrait :
     - le titre : dans <title>, avant le premier " - "
     - le texte d'accroche : dans <meta name="description">
     - l'image : la première <img src="uploads/..."> trouvée
   → aucune information à retaper, elle est déjà dans la page.
4. Ajoute une entrée en tête de `data/nouveautes.json` (source de
   vérité, hébergée dans CE dépôt GitHub).
5. Génère une "page autonome" (sans menu, liens en URLs absolues) dans
   `autonome/`, utilisable telle quelle dans un e-mail.
6. Régénère `nouveautes.xml` (flux RSS, branchable sur un outil de
   newsletter compatible RSS-to-email) et
   `newsletter/<page>-email.html` (bloc HTML à coller à la main dans
   n'importe quel autre outil d'emailing).
7. Commit tout ça dans ce dépôt.

Le site va lui-même chercher `data/nouveautes.json` en direct sur
GitHub à chaque affichage (voir assets/js/nouveautes-render.js) : il
n'y a donc RIEN à recopier dans votre prochain zip de déploiement.

Pour qu'une page NE devienne PAS une nouveauté, ajoutez le commentaire
`<!-- no-nouveaute -->` n'importe où dans son HTML.
"""

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from xml.etree import ElementTree
from xml.sax.saxutils import escape as xml_escape

import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

RACINE = Path(__file__).resolve().parent.parent

SITE_URL = "https://pokao.pages.dev/"
SITEMAP_URL = SITE_URL.rstrip("/") + "/sitemap.xml"

# Les "pages autonomes" ne sont pas déployées sur Cloudflare : elles
# vivent dans ce dépôt GitHub et sont publiées via GitHub Pages, comme
# le faisait pokao2.html avec l'ancien système Weebly. Vérifiez que
# Settings > Pages du dépôt est bien configuré sur "Deploy from a
# branch" > main > / (root).
PAGES_URL = "https://pokaoproductions-collab.github.io/pokao/"

FICHIER_JSON = RACINE / "data" / "nouveautes.json"
FICHIER_MANIFEST = RACINE / "data" / "nouveautes-manifest.json"
FICHIER_RSS = RACINE / "nouveautes.xml"
DOSSIER_AUTONOME = RACINE / "autonome"
DOSSIER_NEWSLETTER = RACINE / "newsletter"

MARQUEUR_EXCLUSION = "no-nouveaute"
ENTETES = {"User-Agent": "Mozilla/5.0 (robot-nouveautes-pokao)"}


# ----------------------------------------------------------------------
# Étape 1 : lire le sitemap en ligne et détecter les nouvelles pages
# ----------------------------------------------------------------------

def lister_pages_sitemap():
    """Renvoie la liste des noms de fichiers (ex. festiv-xxx.html)
    présents dans le sitemap.xml en ligne."""
    reponse = requests.get(SITEMAP_URL, headers=ENTETES, timeout=30)
    reponse.raise_for_status()
    racine_xml = ElementTree.fromstring(reponse.content)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [el.text.strip() for el in racine_xml.findall(".//s:loc", ns) if el.text]
    return sorted(u.rsplit("/", 1)[-1] for u in urls if u)


def charger_manifest():
    if FICHIER_MANIFEST.exists():
        return set(json.loads(FICHIER_MANIFEST.read_text(encoding="utf-8")))
    return None  # None = premier lancement


def enregistrer_manifest(pages_connues):
    FICHIER_MANIFEST.write_text(
        json.dumps(sorted(pages_connues), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


# ----------------------------------------------------------------------
# Étape 2 : extraction automatique des informations d'une page en ligne
# ----------------------------------------------------------------------

def telecharger_page(nom_fichier):
    url = SITE_URL.rstrip("/") + "/" + nom_fichier
    reponse = requests.get(url, headers=ENTETES, timeout=30)
    reponse.raise_for_status()
    reponse.encoding = "utf-8"  # le site est toujours servi en UTF-8
    return reponse.text


def extraire_infos_page(nom_fichier, html_brut):
    soup = BeautifulSoup(html_brut, "lxml")

    titre_tag = soup.find("title")
    titre_brut = titre_tag.get_text().strip() if titre_tag else nom_fichier
    titre = titre_brut.split(" - ")[0].strip()

    meta_desc = soup.find("meta", attrs={"name": "description"})
    texte = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""

    image = ""
    zone = soup.find("main") or soup
    img_tag = zone.find("img", src=re.compile(r"uploads/"))
    if img_tag:
        image = img_tag["src"].lstrip("/")

    return {
        "titre": titre,
        "url": nom_fichier,
        "image": image,
        "texte": texte,
        "date": date.today().isoformat(),
        "autonome": None,
    }, soup


def page_exclue(html_brut):
    return MARQUEUR_EXCLUSION in html_brut


# ----------------------------------------------------------------------
# Étape 3 : "page autonome" (sans nav, pour newsletter) — URLs absolues
# ----------------------------------------------------------------------

def transformer_en_span(a):
    a.name = "span"
    if a.has_attr("href"):
        del a["href"]


def nettoyer_page_autonome(soup):
    header = soup.select_one("header.site-header")
    if header:
        brand = header.select_one("a.brand")
        if brand:
            transformer_en_span(brand)
        nav = header.select_one("nav.main-nav")
        if nav:
            nav.decompose()
        menu_btn = header.select_one("button.menu-button")
        if menu_btn:
            menu_btn.decompose()

    script_nav = soup.select_one('script[src*="home-nav.js"]')
    if script_nav:
        script_nav.decompose()

    for a in soup.select(".eyebrow a"):
        transformer_en_span(a)

    for el in soup.select(".artwork-nav"):
        el.decompose()

    footer_nav = soup.select_one("footer.site-footer nav")
    if footer_nav:
        footer_nav.decompose()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        externe = bool(re.match(r"^([a-z]+:)?//", href, re.I)) or href.startswith(
            ("mailto:", "tel:")
        )
        if not externe:
            transformer_en_span(a)


def ajouter_lien_retour(soup):
    """Ajoute, tout en bas de la page, un lien de retour vers le site
    principal — pour que quelqu'un qui reçoit cette page par e-mail
    puisse toujours revenir facilement sur pokao.pages.dev."""
    body = soup.find("body")
    if not body:
        return
    bloc = soup.new_tag("div")
    bloc["style"] = (
        "text-align:center;padding:32px 16px;margin-top:24px;"
        "font-family:Arial,Helvetica,sans-serif;"
    )
    lien = soup.new_tag("a", href=SITE_URL)
    lien.string = "← Voir sur le site Pokao"
    lien["style"] = "color:#a6432c;text-decoration:none;font-weight:bold;"
    bloc.append(lien)
    body.append(bloc)


def absolutiser_chemins(soup):
    """Toutes les images/scripts/styles de la page autonome pointent
    en absolu vers le site en ligne (elle ne vit pas à côté du site,
    juste dans le dépôt GitHub / un e-mail)."""

    def absolu(chemin):
        if not chemin or re.match(r"^([a-z][a-z0-9+.\-]*:)?//", chemin, re.I):
            return chemin
        if re.match(r"^(data:|mailto:|tel:|javascript:|#)", chemin, re.I):
            return chemin
        return SITE_URL.rstrip("/") + "/" + chemin.lstrip("./")

    for tag, attr in [
        ("img", "src"), ("script", "src"), ("source", "src"), ("iframe", "src"),
        ("link", "href"),
    ]:
        for el in soup.find_all(tag, attrs={attr: True}):
            el[attr] = absolu(el[attr])


def generer_page_autonome(nom_fichier, soup):
    DOSSIER_AUTONOME.mkdir(exist_ok=True)
    nom_sortie = re.sub(r"\.html?$", "", nom_fichier) + "-autonome.html"
    nettoyer_page_autonome(soup)
    ajouter_lien_retour(soup)
    absolutiser_chemins(soup)
    html_final = str(soup)
    if not html_final.lstrip().lower().startswith("<!doctype"):
        html_final = "<!DOCTYPE html>\n" + html_final
    (DOSSIER_AUTONOME / nom_sortie).write_text(html_final, encoding="utf-8")
    return PAGES_URL.rstrip("/") + "/autonome/" + nom_sortie


# ----------------------------------------------------------------------
# Étape 4 : flux RSS + bloc email (branchables sur un outil plus tard)
# ----------------------------------------------------------------------

def regenerer_rss(entrees):
    items_xml = []
    for item in entrees:
        cible = item.get("autonome")
        lien = cible if (cible and cible.startswith("http")) else SITE_URL.rstrip("/") + "/" + item["url"]
        image_abs = SITE_URL.rstrip("/") + "/" + item["image"] if item["image"] else ""
        try:
            pub_date = datetime.fromisoformat(item["date"]).replace(
                tzinfo=timezone.utc
            ).strftime("%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            pub_date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")

        description = xml_escape(item["texte"])
        if image_abs:
            description += f'<br/><img src="{xml_escape(image_abs)}" alt=""/>'

        items_xml.append(
            "  <item>\n"
            f"    <title>{xml_escape(item['titre'])}</title>\n"
            f"    <link>{xml_escape(lien)}</link>\n"
            f"    <guid isPermaLink=\"false\">{xml_escape(item['url'])}</guid>\n"
            f"    <pubDate>{pub_date}</pubDate>\n"
            f"    <description>{description}</description>\n"
            "  </item>"
        )

    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>\n'
        "  <title>Le petit monde de Pokao — Nouveautés</title>\n"
        f"  <link>{xml_escape(SITE_URL)}</link>\n"
        "  <description>Les dernières nouveautés du site POKAO.</description>\n"
        "  <language>fr-fr</language>\n"
        + "\n".join(items_xml)
        + "\n</channel></rss>\n"
    )
    FICHIER_RSS.write_text(rss, encoding="utf-8")


def generer_bloc_email(item):
    lien = item.get("autonome") or (SITE_URL.rstrip("/") + "/" + item["url"])
    img_abs = SITE_URL.rstrip("/") + "/" + item["image"] if item["image"] else ""
    texte_html = (
        f'<p style="margin:0 0 20px;font-size:14px;line-height:1.5;color:#665f57;">{item["texte"]}</p>'
        if item["texte"] else ""
    )
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
        'style="max-width:600px;margin:0 auto;font-family:Arial,Helvetica,sans-serif;'
        'background:#ffffff;border:1px solid #e0d8c9;border-radius:10px;overflow:hidden;">\n'
        "  <tr><td style=\"padding:0;\">\n"
        f'    <a href="{lien}" style="text-decoration:none;">\n'
        f'      <img src="{img_abs}" alt="{item["titre"]}" width="600" '
        'style="display:block;width:100%;max-width:600px;height:auto;border:0;">\n'
        "    </a>\n  </td></tr>\n"
        '  <tr><td style="padding:24px 28px;">\n'
        '    <p style="margin:0 0 8px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;'
        'color:#a6432c;font-weight:bold;">Nouveauté</p>\n'
        f'    <p style="margin:0 0 10px;font-size:20px;line-height:1.3;color:#2b2622;'
        f'font-weight:bold;">{item["titre"]}</p>\n'
        f"    {texte_html}\n"
        f'    <a href="{lien}" style="display:inline-block;padding:10px 20px;'
        'background:#a6432c;color:#ffffff;text-decoration:none;font-size:14px;'
        'font-weight:bold;border-radius:6px;">Découvrir →</a>\n'
        "  </td></tr>\n</table>\n"
    )


def enregistrer_bloc_email(item):
    DOSSIER_NEWSLETTER.mkdir(exist_ok=True)
    nom_sortie = re.sub(r"\.html?$", "", item["url"]) + "-email.html"
    (DOSSIER_NEWSLETTER / nom_sortie).write_text(generer_bloc_email(item), encoding="utf-8")


# ----------------------------------------------------------------------
# Programme principal
# ----------------------------------------------------------------------

def main():
    entrees = json.loads(FICHIER_JSON.read_text(encoding="utf-8")) if FICHIER_JSON.exists() else []

    try:
        pages_actuelles = set(lister_pages_sitemap())
    except Exception as exc:  # sitemap injoignable : on ne casse rien
        print(f"Impossible de lire {SITEMAP_URL} : {exc}")
        return

    manifest = charger_manifest()
    premier_lancement = manifest is None

    if premier_lancement:
        enregistrer_manifest(pages_actuelles)
        print(f"Premier lancement : {len(pages_actuelles)} page(s) mémorisée(s) comme déjà connues.")
        regenerer_rss(entrees)
        return

    nouvelles_pages = sorted(pages_actuelles - manifest)
    if not nouvelles_pages:
        print("Aucune nouvelle page détectée.")
        return

    for nom_fichier in nouvelles_pages:
        try:
            html_brut = telecharger_page(nom_fichier)
        except Exception as exc:
            print(f"  {nom_fichier} : impossible à télécharger ({exc}), ignorée pour l'instant.")
            continue

        if page_exclue(html_brut):
            print(f"  {nom_fichier} : exclue via <!-- no-nouveaute -->, ignorée.")
            manifest.add(nom_fichier)
            continue

        item, soup = extraire_infos_page(nom_fichier, html_brut)
        item["autonome"] = generer_page_autonome(nom_fichier, soup)
        entrees.insert(0, item)
        enregistrer_bloc_email(item)
        manifest.add(nom_fichier)
        print(f"  + Nouveauté détectée : {item['titre']}  ({nom_fichier})")

    enregistrer_manifest(manifest)
    FICHIER_JSON.write_text(
        json.dumps(entrees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    regenerer_rss(entrees)


if __name__ == "__main__":
    sys.exit(main())
