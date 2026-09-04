# Robot des nouveautés — mode d'emploi (v2 : sans dépôt du site)

Ce système remplace `moulinette-nouveautes.html` : plus besoin de retaper
le titre, l'image et le texte d'une nouvelle page dans un outil à part —
et sans dépendre de git pour votre site. Votre méthode de déploiement
actuelle (créer un zip et l'envoyer via "Créer un déploiement" sur le
tableau de bord Cloudflare) reste **entièrement inchangée**.

## Comment ça marche, au quotidien

1. Vous créez une nouvelle page HTML comme d'habitude (`festiv-xxx.html`,
   `menez-2027.html`, etc.), avec son `<title>`, son
   `<meta name="description">` et son `<h1 id="paint-title">` habituels.
2. **Juste avant de créer votre zip**, double-cliquez sur
   `lancer_generer_sitemap.bat` (à la racine du site) — il met à jour
   `sitemap.xml` avec la liste de vos pages. Puis déployez comme
   d'habitude.
3. Le robot GitHub (hébergé dans le dépôt `pokaoproductions-collab/pokao`,
   séparé de votre site) se réveille tout seul toutes les 6h et :
   - télécharge `sitemap.xml` sur le site en ligne ;
   - repère les pages qu'il ne connaît pas encore ;
   - télécharge chacune, et en extrait le titre, la description et la
     première image — sans que vous les retapiez nulle part ;
   - ajoute une entrée dans `data/nouveautes.json` (hébergé dans ce
     dépôt GitHub) ;
   - génère une **page autonome** (sans menu, en URLs absolues) dans
     `autonome/`, utilisable dans un e-mail ;
   - régénère `nouveautes.xml` (flux RSS) et
     `newsletter/<page>-email.html` (bloc HTML prêt à coller dans un
     outil d'emailing).
4. **Rien d'autre à faire.** Votre site va lui-même chercher
   `data/nouveautes.json` en direct sur GitHub à chaque affichage (voir
   `assets/js/nouveautes-render.js`), donc dès que le robot a mis à
   jour ce fichier, le bandeau "Nouveauté" de votre site le reflète
   automatiquement — sans nouveau déploiement.

Vous n'ouvrez plus jamais `moulinette-nouveautes.html`, et vous pouvez
même retirer `<script src="assets/js/nouveautes-data.js">` de vos pages
si vous voulez faire le ménage (il n'est plus utilisé) — mais ce n'est
pas obligatoire, le laisser ne gêne en rien.

## GitHub Pages : à vérifier, pas à désactiver

Les "pages autonomes" (`autonome/*.html`) ne sont pas déployées sur
Cloudflare : elles vivent dans ce dépôt et sont publiées via
**GitHub Pages**, exactement comme le faisait `pokao2.html` avec
l'ancien système Weebly — sauf qu'elles sont maintenant remplies
automatiquement. Vérifiez que **Settings → Pages** est bien réglé sur
*Deploy from a branch → main → / (root)*. Si un déploiement GitHub
Pages était déjà actif (visible dans l'onglet Code sous
"Deployments"), c'est bon signe : c'est ce même mécanisme qui sert ici,
pas la peine d'y toucher.

## Si une page ne doit PAS devenir une nouveauté

Ajoutez le commentaire `<!-- no-nouveaute -->` n'importe où dans son
HTML. Le robot l'ignorera (elle restera dans le sitemap, juste pas
dans les nouveautés).

## Envie d'une vérification immédiate au lieu d'attendre 6h ?

Sur GitHub : onglet **Actions** → **Robot des nouveautés POKAO** →
bouton **Run workflow**. Il se lance dans la minute.

## Pour la newsletter, quand vous choisirez un outil

- **Outils compatibles RSS-to-email** (Brevo, Mailchimp, Buttondown...) :
  donnez-leur l'adresse
  `https://raw.githubusercontent.com/pokaoproductions-collab/pokao/main/nouveautes.xml`
  — ils enverront un e-mail à chaque nouvelle entrée, automatiquement.
- **N'importe quel autre outil** : ouvrez le fichier
  `newsletter/<page>-email.html` correspondant dans le dépôt GitHub et
  collez son contenu dans l'éditeur HTML de l'outil.

## Mise en place, à faire une fois

Le dépôt `pokaoproductions-collab/pokao` ne doit contenir QUE les
fichiers de ce zip (pas votre site) :

1. Assurez-vous d'avoir bien supprimé les anciens fichiers du scraper
   Weebly (`extract*.py`, `config_pokao2.json`, `nouveaute*.json`,
   `.github/workflows/extract.yml`, et les vieux `index.html` /
   `pokao.html` / `pokao2.html` si vous ne vous en servez pas ailleurs).
2. Déposez le contenu de ce zip dans le dépôt (via l'interface web
   github.com, fichier par fichier ou via "Add file → Upload files").
3. Sur GitHub : **Settings → Actions → General → Workflow permissions**
   → cochez *Read and write permissions*.
4. Dans votre dossier de site local, ajoutez `scripts/generer_sitemap.py`
   et `lancer_generer_sitemap.bat` (fournis dans ce zip), et
   remplacez `assets/js/nouveautes-render.js` par la version fournie.
5. Lancez `lancer_generer_sitemap.bat` une première fois, incluez
   `sitemap.xml` dans votre prochain zip, et déployez normalement sur
   Cloudflare.
6. Sur GitHub, lancez le robot une première fois à la main (Actions →
   Run workflow) : il ne créera **aucune** nouveauté (il mémorise juste
   vos pages actuelles comme déjà connues). C'est normal.
7. À partir de la prochaine page que vous créerez : tout est automatique.

## Fichiers

Dans le dépôt GitHub `pokaoproductions-collab/pokao` :
```
scripts/generate_nouveautes.py   ← le robot lui-même
scripts/requirements.txt
.github/workflows/nouveautes-auto.yml
data/nouveautes.json             ← source de vérité, lue en direct par le site
data/nouveautes-manifest.json    ← mémoire des pages déjà connues (générée seule)
autonome/                        ← pages "propres" générées pour la newsletter
newsletter/                      ← blocs HTML prêts à coller dans un e-mail
nouveautes.xml                   ← flux RSS des nouveautés
```

Dans votre dossier de site local (à ajouter/remplacer) :
```
scripts/generer_sitemap.py       ← à lancer avant chaque déploiement
lancer_generer_sitemap.bat       ← raccourci pour le lancer facilement
sitemap.xml                      ← généré par le script ci-dessus
assets/js/nouveautes-render.js   ← remplacé : va chercher les données sur GitHub
```
