"""
Pipeline principal de scraping d'offres d'emploi.
Orchestre les différentes sources et applique les filtres.
"""
import sys
from typing import List, Dict, Callable, Optional
from datetime import datetime
from playwright.sync_api import sync_playwright
from scraper.db import DatabaseManager
from scraper.utils import (
    is_recent, is_valid_location, matches_keywords,
    categorize_role, detect_keywords, clean_text
)
from scraper.sources.indeed_scraper import IndeedScraper
from scraper.sources.wttj_scraper import WTTJScraper
from scraper.sources.linkedin_scraper import LinkedInScraper
from scraper.sources.hellowork_scraper import HelloWorkScraper
from scraper.sources.apec_scraper import APECScraper
from scraper.sources.glassdoor_scraper import GlassdoorScraper
from scraper.sources.search_scraper import SearchScraper
from config import HEADLESS, BROWSER_TIMEOUT


class ScrapingPipeline:
    """Pipeline de scraping orchestrant toutes les sources."""
    
    def __init__(self):
        """Initialise le pipeline."""
        self.db = DatabaseManager()
        self.sources = [
            IndeedScraper(),
            WTTJScraper(),
            LinkedInScraper(),
            HelloWorkScraper(),
            APECScraper(),
            GlassdoorScraper(),
            SearchScraper()
        ]
    
    def run(self, country: str = "France", location: str = "France", queries: Optional[List[str]] = None, progress_callback: Optional[Callable] = None) -> Dict:
        """
        Exécute le pipeline complet de scraping.
        """
        # Fix redondant pour Windows au cas où le thread Streamlit l'outrepasse
        if sys.platform == 'win32':
            try:
                import asyncio
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            except Exception:
                pass

        self._log("🚀 Démarrage du pipeline de scraping...", progress_callback)
        
        # Collecter les offres de toutes les sources
        all_raw_jobs = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            
            for source in self.sources:
                self._log(f"\n📡 Source: {source.source_name}", progress_callback)
                
                try:
                    jobs = source.scrape(browser, country=country, location=location, queries=queries, progress_callback=progress_callback)
                    all_raw_jobs.extend(jobs)
                    self._log(f"✅ {source.source_name}: {len(jobs)} offres récupérées", progress_callback)
                except Exception as e:
                    self._log(f"❌ {source.source_name}: Erreur - {str(e)}", progress_callback)
                    continue
            
            browser.close()
        
        self._log(f"\n📊 Total brut: {len(all_raw_jobs)} offres", progress_callback)
        
        # Filtrer et enrichir les offres
        self._log("\n🔍 Filtrage et enrichissement...", progress_callback)
        filtered_jobs = self._filter_and_enrich(all_raw_jobs, location, progress_callback)
        
        self._log(f"✅ Offres valides: {len(filtered_jobs)}", progress_callback)
        self._log(f"❌ Offres filtrées: {len(all_raw_jobs) - len(filtered_jobs)}", progress_callback)
        
        # Sauvegarder en base
        self._log("\n💾 Sauvegarde en base de données...", progress_callback)
        db_stats = self.db.bulk_upsert(filtered_jobs)
        
        self._log(f"✅ Nouvelles offres: {db_stats['added']}", progress_callback)
        self._log(f"🔄 Offres mises à jour: {db_stats['updated']}", progress_callback)
        self._log(f"⏭️  Doublons ignorés: {db_stats['skipped']}", progress_callback)
        
        # Statistiques finales
        stats = {
            **db_stats,
            'total_scraped': len(all_raw_jobs),
            'filtered_out': len(all_raw_jobs) - len(filtered_jobs)
        }
        
        self._log("\n✨ Pipeline terminé!", progress_callback)
        return stats
    
    def _filter_and_enrich(self, raw_jobs: List[Dict], target_location: str = "France", progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Filtre et enrichit les offres brutes.
        """
        filtered = []
        
        for job in raw_jobs:
            # Filtre 1: Date récente (≤ 3 jours)
            if job.get('published_date'):
                if not is_recent(job['published_date']):
                    continue
            
            # Filtre 2: Localisation
            location = job.get('location', '')
            if not is_valid_location(location, target_location):
                continue
            
            # Filtre 3: Mots-clés pertinents
            search_text = f"{job.get('job_title', '')} {job.get('snippet', '')}"
            if not matches_keywords(search_text):
                continue
            
            # Enrichissement 1: Catégorisation du rôle
            job['role_category'] = categorize_role(search_text)
            
            # Enrichissement 2: Détection des mots-clés
            keywords = detect_keywords(search_text)
            job['detected_keywords'] = ', '.join(sorted(keywords))
            
            # Enrichissement 3: Timestamp de scraping
            job['scraped_at'] = datetime.utcnow()
            
            filtered.append(job)
        
        return filtered
    
    def _log(self, message: str, progress_callback: Optional[Callable] = None):
        """Log un message."""
        if progress_callback:
            progress_callback(message)
        else:
            print(message)
    
    def get_all_jobs(self, limit: Optional[int] = None) -> List[Dict]:
        """Récupère toutes les offres de la base."""
        return self.db.get_all_jobs(limit)
    
    def get_statistics(self) -> Dict:
        """Récupère les statistiques."""
        return self.db.get_statistics()
    
    def update_job_status(self, job_id: int, applied: bool) -> bool:
        """Met à jour le statut de candidature d'une offre."""
        return self.db.update_job_status(job_id, applied)
