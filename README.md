# 🔍 Job Crawler - Scraping d'Offres Data France

Application Streamlit complète pour scraper automatiquement des offres d'emploi data en France, avec interface dark mode moderne, dashboard statistiques et tableau interactif.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.41+-green.svg)

## 📋 Table des Matières

- [Fonctionnalités](#-fonctionnalités)
- [Stack Technique](#-stack-technique)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Architecture](#-architecture)
- [Ajouter une Nouvelle Source](#-ajouter-une-nouvelle-source)
- [Configuration](#-configuration)
- [Dépannage](#-dépannage)

## ✨ Fonctionnalités

### Scraping Intelligent
- ✅ **Multi-sources** : Indeed, Welcome to the Jungle, LinkedIn
- ✅ **Filtrage automatique** : Offres publiées dans les 3 derniers jours
- ✅ **Géolocalisation** : Uniquement France (villes, régions, remote)
- ✅ **Détection de rôles** : Data Analyst, Business Analyst, Data Engineer
- ✅ **Déduplication** : Évite les doublons par URL ou hash

### Interface Moderne
- 🎨 **Dark Mode** : Interface élégante avec fond noir
- 📊 **Dashboard Statistiques** : Métriques, graphiques interactifs
- 🔍 **Tableau Filtrable** : Recherche, tri, filtres par catégorie/source
- 📥 **Export CSV** : Téléchargement des résultats
- 🚀 **Logs en Temps Réel** : Suivi du scraping en direct

### Robustesse
- 🔄 **Retry Logic** : Réessais automatiques en cas d'échec
- 🛡️ **Anti-Détection** : User agents rotatifs, délais aléatoires
- ⚠️ **Gestion d'Erreurs** : Continue même si une source échoue
- 💾 **Base SQLite** : Stockage persistant local

## 🛠️ Stack Technique

- **Frontend** : Streamlit (interface web)
- **Scraping** : Playwright (navigateur headless) + BeautifulSoup
- **Base de Données** : SQLite (fichier local)
- **Data Processing** : pandas, SQLAlchemy
- **Visualisation** : Plotly
- **Parsing Dates** : python-dateutil

## 📦 Installation

### Prérequis
- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes

1. **Cloner ou télécharger le projet**
```bash
cd JobCrawler
```

2. **Créer un environnement virtuel**
```bash
python -m venv .venv
```

3. **Activer l'environnement virtuel**

Windows :
```bash
.venv\Scripts\activate
```

macOS/Linux :
```bash
source .venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

5. **Installer les navigateurs Playwright**
```bash
playwright install chromium
```

## 🚀 Utilisation

### Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`.

### Workflow

1. **Cliquer sur "🚀 Craquer les offres"**
   - Le scraping démarre automatiquement
   - Les logs s'affichent en temps réel
   - Durée : 2-5 minutes selon les sources

2. **Consulter les statistiques**
   - Total d'offres
   - Répartition par catégorie (Data Analyst, Business Analyst, Data Engineer)
   - Répartition par source
   - Évolution par jour
   - Top localisations

3. **Explorer le tableau**
   - Filtrer par catégorie, source
   - Rechercher par titre ou entreprise
   - Cliquer sur les URLs pour voir les offres

4. **Exporter les résultats**
   - Bouton "📥 Exporter en CSV"
   - Fichier téléchargé avec toutes les offres filtrées

## 🏗️ Architecture

```
JobCrawler/
├── app.py                      # Application Streamlit principale
├── config.py                   # Configuration centralisée
├── requirements.txt            # Dépendances Python
├── jobs.db                     # Base de données SQLite (créée automatiquement)
├── scraper/
│   ├── __init__.py
│   ├── db.py                   # Modèles SQLAlchemy et gestion DB
│   ├── utils.py                # Fonctions utilitaires
│   ├── pipeline.py             # Orchestrateur principal
│   └── sources/
│       ├── __init__.py
│       ├── base.py             # Interface abstraite SourceScraper
│       ├── indeed_scraper.py   # Scraper Indeed France
│       ├── wttj_scraper.py     # Scraper Welcome to the Jungle
│       └── linkedin_scraper.py # Scraper LinkedIn Jobs
└── README.md
```

### Flux de Données

```
[Sources Web] → [Scrapers] → [Pipeline] → [Filtres] → [Enrichissement] → [SQLite] → [Streamlit UI]
```

1. **Scrapers** : Chaque source (Indeed, WTTJ, LinkedIn) extrait les offres
2. **Pipeline** : Orchestre les scrapers, collecte les données brutes
3. **Filtres** : Applique les critères (France, 3 jours, mots-clés)
4. **Enrichissement** : Catégorise les rôles, détecte les mots-clés
5. **SQLite** : Stocke avec déduplication
6. **Streamlit** : Affiche dashboard + tableau

## 🔧 Ajouter une Nouvelle Source

### Étape 1 : Créer le Scraper

Créez un fichier `scraper/sources/nouvelle_source.py` :

```python
from typing import List, Dict, Optional, Callable
from playwright.sync_api import Browser
from scraper.sources.base import SourceScraper
from scraper.utils import parse_relative_date, clean_text, extract_snippet, normalize_url

class NouvelleSourceScraper(SourceScraper):
    """Scraper pour Nouvelle Source."""
    
    def __init__(self):
        super().__init__("NouvelleSource")
        self.base_url = "https://example.com"
    
    def scrape(self, browser: Browser, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Scrappe les offres."""
        jobs = []
        page = self._create_page(browser)
        
        try:
            # 1. Naviguer vers la page
            page.goto(f"{self.base_url}/jobs?q=data&location=France", timeout=30000)
            
            # 2. Attendre le chargement
            page.wait_for_selector('.job-card', timeout=10000)
            
            # 3. Extraire les offres
            job_cards = page.query_selector_all('.job-card')
            
            for card in job_cards:
                # Extraire les données
                title = self._safe_get_text(card.query_selector('.title'))
                company = self._safe_get_text(card.query_selector('.company'))
                location = self._safe_get_text(card.query_selector('.location'))
                url = self._safe_get_attribute(card.query_selector('a'), 'href')
                
                jobs.append({
                    'job_title': clean_text(title),
                    'company': clean_text(company),
                    'location': clean_text(location),
                    'url': normalize_url(url),
                    'published_date': None,  # Parser si disponible
                    'snippet': '',
                    'source': self.source_name
                })
        
        finally:
            page.close()
        
        return jobs
```

### Étape 2 : Enregistrer dans le Pipeline

Modifiez `scraper/pipeline.py` :

```python
from scraper.sources.nouvelle_source import NouvelleSourceScraper

class ScrapingPipeline:
    def __init__(self):
        self.db = DatabaseManager()
        self.sources = [
            IndeedScraper(),
            WTTJScraper(),
            LinkedInScraper(),
            NouvelleSourceScraper()  # ← Ajouter ici
        ]
```

### Étape 3 : Tester

Relancez l'application et cliquez sur "Craquer les offres". La nouvelle source sera automatiquement scrapée.

## ⚙️ Configuration

Modifiez `config.py` pour personnaliser :

### Mots-clés
```python
KEYWORDS = {
    'data_analyst': ['data analyst', 'analyste de données'],
    'business_analyst': ['business analyst', 'analyste business'],
    'data_engineer': ['data engineer', 'ingénieur données'],
    # Ajouter vos mots-clés
}
```

### Fenêtre Temporelle
```python
MAX_DAYS_OLD = 3  # Modifier pour 7 jours, etc.
```

### Mode Headless
```python
HEADLESS = True  # False pour voir le navigateur
```

### Localisations
```python
FRENCH_LOCATIONS = [
    'france', 'paris', 'lyon', 'marseille',
    # Ajouter vos villes
]
```

## 🐛 Dépannage

### Erreur : "playwright not found"
```bash
playwright install chromium
```

### Erreur : "Module not found"
Vérifiez que l'environnement virtuel est activé :
```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

### Aucune offre trouvée
- Vérifiez votre connexion Internet
- Certaines sources peuvent bloquer le scraping (captcha, 403)
- Essayez avec `HEADLESS = False` dans `config.py` pour déboguer

### Base de données corrompue
Supprimez `jobs.db` et relancez l'application :
```bash
rm jobs.db  # macOS/Linux
del jobs.db  # Windows
```

### Scraping très lent
- Réduisez `REQUEST_DELAY_MAX` dans `config.py`
- Commentez certaines sources dans `pipeline.py`

## 📊 Données Stockées

Chaque offre contient :
- **job_title** : Titre de l'offre
- **company** : Entreprise
- **role_category** : Data Analyst / Business Analyst / Data Engineer / Other
- **source** : Indeed / WTTJ / LinkedIn
- **published_date** : Date de publication (ISO)
- **location** : Ville/région/remote
- **url** : Lien direct (clé unique)
- **snippet** : Résumé court
- **detected_keywords** : Mots-clés détectés
- **scraped_at** : Timestamp de scraping

## 🔒 Considérations Légales

⚠️ **Important** : Ce projet est à usage éducatif et personnel.

- Respectez les conditions d'utilisation des sites scrapés
- Ne surchargez pas les serveurs (délais entre requêtes)
- Certains sites interdisent le scraping automatisé
- Utilisez de manière responsable et éthique

## 📝 Licence

Ce projet est fourni "tel quel" sans garantie. Utilisez-le à vos propres risques.

## 🤝 Contribution

Pour améliorer le projet :
1. Ajoutez de nouvelles sources (voir section ci-dessus)
2. Améliorez les sélecteurs CSS (les sites changent régulièrement)
3. Optimisez les performances
4. Ajoutez des tests unitaires

## 📧 Support

En cas de problème :
1. Vérifiez la section [Dépannage](#-dépannage)
2. Consultez les logs dans l'interface Streamlit
3. Vérifiez que les dépendances sont à jour

---

**Bon scraping ! 🚀**
