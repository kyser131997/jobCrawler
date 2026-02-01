# Déploiement sur Streamlit Cloud

Ce guide explique comment déployer l'application **Job Crawler** sur Streamlit Community Cloud.

## 1. Prérequis GitHub
Assurez-vous que votre code est poussé sur un dépôt GitHub public ou privé.
Le dépôt doit contenir les fichiers suivants à la racine :
- `app.py`
- `requirements.txt`
- `packages.txt`
- `scraper/` (dossier)

## 2. Configuration Streamlit Cloud

1. Connectez-vous à [share.streamlit.io](https://share.streamlit.io/).
2. Cliquez sur **"New app"**.
3. Sélectionnez votre dépôt GitHub, la branche (ex: `main`), et le fichier principal (`app.py`).
4. **Important** : Avant de cliquer sur "Deploy", ouvrez la section **"Advanced settings"** (si disponible pour les secrets, sinon ignorez).

## 3. Secrets (Optionnel)
Si vous aviez des clés API privées (ce qui n'est pas le cas pour ce projet public Algolia), vous les ajouteriez dans les "Secrets". Ici, aucune configuration secrète n'est requise car les clés Algolia de WTTJ sont publiques.

## 4. Déploiement
Cliquez sur **"Deploy"**.

Streamlit va :
1. Installer les dépendances Python listées dans `requirements.txt`.
2. Installer les paquets Linux listés dans `packages.txt` (Chromium).
3. Lancer `app.py`.
4. Au premier démarrage, le script `app.py` vérifiera et installera les binaires Playwright manquants (cela peut prendre quelques minutes au premier lancement).

## Dépannage
- Si le scraping échoue avec une erreur de navigateur, vérifiez les logs dans la console Streamlit Cloud (en bas à droite).
- Le redémarrage de l'app ("Reboot app") résout souvent les problèmes d'installation initiale.
