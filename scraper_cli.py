"""
Script CLI pour exécuter le pipeline de scraping de manière isolée.
Cela évite les conflits d'event loop asyncio avec Streamlit sur Windows.
"""
import sys
import asyncio
from typing import List, Dict, Optional, Callable

# Fix essentiel pour Windows
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

import argparse
from scraper.pipeline import ScrapingPipeline

def main():
    parser = argparse.ArgumentParser(description="Exécuter le pipeline de scraping.")
    parser.add_argument("--country", type=str, default="France", help="Pays cible")
    parser.add_argument("--location", type=str, default="France", help="Région ou ville cible")
    parser.add_argument("--queries", type=str, default="", help="Mots-clés de recherche séparés par des virgules")
    args = parser.parse_args()

    print(f"🚀 Démarrage du scraper en mode isolé ({args.country}, {args.location})...")
    pipeline = ScrapingPipeline()
    
    # Définir un callback simple pour les logs dans le terminal
    def cli_callback(message):
        print(message)
    
    # Parser les queries
    queries_list = [q.strip() for q in args.queries.split(",")] if args.queries else None
    
    try:
        stats = pipeline.run(country=args.country, location=args.location, queries=queries_list, progress_callback=cli_callback)
        print("\n✨ Scraping terminé avec succès!")
        print(f"📊 Stats: {stats}")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
