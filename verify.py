"""
Script de vérification rapide pour tester les imports et la structure.
"""
import sys

print("🔍 Vérification de l'installation...\n")

# Test des imports principaux
try:
    import streamlit as st
    print("✅ Streamlit importé")
except ImportError as e:
    print(f"❌ Erreur Streamlit: {e}")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright
    print("✅ Playwright importé")
except ImportError as e:
    print(f"❌ Erreur Playwright: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print("✅ Pandas importé")
except ImportError as e:
    print(f"❌ Erreur Pandas: {e}")
    sys.exit(1)

try:
    import plotly.express as px
    print("✅ Plotly importé")
except ImportError as e:
    print(f"❌ Erreur Plotly: {e}")
    sys.exit(1)

try:
    from sqlalchemy import create_engine
    print("✅ SQLAlchemy importé")
except ImportError as e:
    print(f"❌ Erreur SQLAlchemy: {e}")
    sys.exit(1)

# Test des modules locaux
try:
    from scraper.db import DatabaseManager
    print("✅ Module scraper.db importé")
except ImportError as e:
    print(f"❌ Erreur scraper.db: {e}")
    sys.exit(1)

try:
    from scraper.utils import is_recent, is_valid_location
    print("✅ Module scraper.utils importé")
except ImportError as e:
    print(f"❌ Erreur scraper.utils: {e}")
    sys.exit(1)

try:
    from scraper.pipeline import ScrapingPipeline
    print("✅ Module scraper.pipeline importé")
except ImportError as e:
    print(f"❌ Erreur scraper.pipeline: {e}")
    sys.exit(1)

try:
    from scraper.sources.indeed_scraper import IndeedScraper
    from scraper.sources.wttj_scraper import WTTJScraper
    from scraper.sources.linkedin_scraper import LinkedInScraper
    print("✅ Tous les scrapers importés")
except ImportError as e:
    print(f"❌ Erreur scrapers: {e}")
    sys.exit(1)

# Test de la base de données
try:
    db = DatabaseManager()
    print("✅ Base de données initialisée")
    
    # Vérifier que la table existe
    stats = db.get_statistics()
    print(f"✅ Base de données fonctionnelle (Total: {stats['total']} offres)")
except Exception as e:
    print(f"❌ Erreur base de données: {e}")
    sys.exit(1)

print("\n✨ Toutes les vérifications sont passées!")
print("\n📝 Pour lancer l'application:")
print("   streamlit run app.py")
