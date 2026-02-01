"""
Scraper pour Welcome to the Jungle (via Algolia API).
"""
import requests
import json
import time
from typing import List, Dict, Optional, Callable
from datetime import datetime
from playwright.sync_api import Browser
from scraper.sources.base import SourceScraper
from scraper.utils import clean_text

class WTTJScraper(SourceScraper):
    """Scraper pour Welcome to the Jungle utilisant l'API Algolia."""
    
    # Configuration Algolia récupérée du site
    ALGOLIA_APP_ID = "CSEKHVMS53"
    ALGOLIA_API_KEY = "4bd8f6215d0cc52b26430765769e65a0"
    INDEX_NAME = "wttj_jobs_production_fr_published_at_desc"
    
    def __init__(self):
        super().__init__("WTTJ")
        self.search_queries = [
            "data analyst",
            "business analyst",
            "data engineer",
            "data scientist",
            "analytics engineer"
        ]
        self.headers = {
            "X-Algolia-Application-Id": self.ALGOLIA_APP_ID,
            "X-Algolia-API-Key": self.ALGOLIA_API_KEY,
            "Content-Type": "application/json",
            "Referer": "https://www.welcometothejungle.com/"
        }
    
    def scrape(self, browser: Browser, country: str = "France", location: str = "France", queries: Optional[List[str]] = None, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Scrappe les offres de Welcome to the Jungle via API.
        Note: Les arguments browser, country, et location sont gardés pour compatibilité 
        mais 'country' et 'location' sont fixés à la France par configuration d'index.
        """
        all_jobs = []
        
        # URL de l'API Algolia
        api_url = f"https://{self.ALGOLIA_APP_ID.lower()}-dsn.algolia.net/1/indexes/{self.INDEX_NAME}/query"
        
        # Utiliser les requêtes fournies ou celles par défaut
        queries_to_use = queries if queries else self.search_queries
        
        for query in queries_to_use:
            self._log_progress(f"Recherche API: {query}", progress_callback)
            
            try:
                # Paramètres de recherche Algolia
                params = {
                    "query": query,
                    "hitsPerPage": 50,  # Récupérer plus d'offres d'un coup
                    "filters": "published_at_timestamp > " + str(int(time.time()) - 3 * 86400) # Offres des 3 derniers jours
                }
                
                payload = {
                    "params": "&".join([f"{k}={v}" for k, v in params.items()])
                }
                
                response = requests.post(api_url, headers=self.headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get("hits", [])
                    self._log_progress(f"  - {len(hits)} résultats trouvés", progress_callback)
                    
                    for hit in hits:
                        job = self._process_hit(hit)
                        if job:
                            all_jobs.append(job)
                else:
                    self._log_progress(f"Erreur API {response.status_code}: {response.text}", progress_callback)
                    
            except Exception as e:
                self._log_progress(f"Erreur lors de la requête pour '{query}': {str(e)}", progress_callback)
            
            # Petit délai pour être gentil avec l'API
            time.sleep(0.5)
            
        self._log_progress(f"Total WTTJ: {len(all_jobs)} offres récupérées", progress_callback)
        return all_jobs
    
    def _process_hit(self, hit: Dict) -> Optional[Dict]:
        """Convertit un résultat Algolia en format d'offre standard."""
        try:
            # Extraction des données
            title = hit.get("name")
            if not title:
                return None
                
            org = hit.get("organization", {})
            company = org.get("name", "Non spécifié")
            
            # Localisation
            offices = hit.get("offices", [])
            location = "France"
            if offices:
                # Prend la première ville disponible
                location = f"{offices[0].get('city', '')}".strip()
                if not location:
                    location = offices[0].get('country', "France")
            
            # Construction de l'URL
            # Format: https://www.welcometothejungle.com/fr/companies/{org_slug}/jobs/{job_slug}
            org_slug = org.get("slug")
            job_slug = hit.get("slug")
            url = ""
            if org_slug and job_slug:
                url = f"https://www.welcometothejungle.com/fr/companies/{org_slug}/jobs/{job_slug}"
            
            # Date
            published_at = hit.get("published_at")
            if published_at:
                # Format ISO retourné par Algolia: 2024-01-31T10:00:00Z
                try:
                    dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    # On garde l'objet datetime pour la compatibilité
                    published_date = dt
                except ValueError:
                    published_date = datetime.now()
            else:
                published_date = datetime.now()

            return {
                'job_title': clean_text(title),
                'company': clean_text(company),
                'location': clean_text(location),
                'published_date': published_date,
                'url': url,
                'snippet': clean_text(org.get("summary", "")[:200] + "..."),
                'source': self.source_name
            }
            
        except Exception:
            return None
