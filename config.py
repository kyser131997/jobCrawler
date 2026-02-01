"""
Configuration centrale pour l'application de scraping d'offres d'emploi.
"""

# Mots-clés pour la détection des offres
KEYWORDS = {
    'data_analyst': ['data analyst', 'analyste de données', 'analyste données'],
    'business_analyst': ['business analyst', 'analyste business', 'analyste métier'],
    'data_engineer': ['data engineer', 'ingénieur données', 'ingénieur data'],
    'data_general': ['data', 'données'],
    'business_general': ['business']
}

# Catégories de rôles (ordre de priorité)
ROLE_CATEGORIES = {
    'Data Engineer': ['data engineer', 'ingénieur données', 'ingénieur data'],
    'Data Analyst': ['data analyst', 'analyste de données', 'analyste données'],
    'Business Analyst': ['business analyst', 'analyste business', 'analyste métier'],
    'Other': []  # Fallback pour les matches génériques
}

# Fenêtre temporelle (en jours)
MAX_DAYS_OLD = 3

# Localisations françaises (mots-clés pour la détection)
FRENCH_LOCATIONS = [
    'france', 'paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes',
    'strasbourg', 'montpellier', 'bordeaux', 'lille', 'rennes', 'reims',
    'le havre', 'saint-étienne', 'toulon', 'grenoble', 'dijon', 'angers',
    'nîmes', 'villeurbanne', 'clermont-ferrand', 'aix-en-provence',
    'brest', 'limoges', 'tours', 'amiens', 'perpignan', 'metz', 'besançon',
    'orléans', 'rouen', 'mulhouse', 'caen', 'nancy', 'argenteuil',
    'montreuil', 'saint-denis', 'île-de-france', 'idf', 'remote france',
    'télétravail', 'full remote', 'distanciel', 'france', 'bruges', 'bègles',
    'mérignac', 'pessac', 'talence', 'villenave-d\'ornon'
]

# Configuration Playwright
HEADLESS = True  # Mode headless pour le navigateur
BROWSER_TIMEOUT = 30000  # Timeout en millisecondes
PAGE_LOAD_TIMEOUT = 20000  # Timeout pour le chargement des pages

# Gestion des erreurs et retry
MAX_RETRIES = 3
RETRY_DELAY = 2  # Secondes entre les tentatives
REQUEST_DELAY_MIN = 1  # Délai minimum entre les requêtes (secondes)
REQUEST_DELAY_MAX = 3  # Délai maximum entre les requêtes (secondes)

# User agents (rotation pour éviter la détection)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

# Base de données
DATABASE_PATH = 'jobs.db'

# Limite d'affichage dans le tableau
MAX_TABLE_ROWS = 500
