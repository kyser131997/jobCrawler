"""
Scraper pour HelloWork.
"""
import logging
import time
import random
from typing import List, Dict, Optional, Callable
from playwright.sync_api import Browser
from scraper.sources.base import SourceScraper
from scraper.utils import parse_relative_date

logger = logging.getLogger(__name__)

class HelloWorkScraper(SourceScraper):
    def __init__(self):
        super().__init__("HelloWork")
        self.base_url = "https://www.hellowork.com"
        
    def scrape(self, browser: Browser, country: str = "France", location: str = "France", progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Scrape les offres de HelloWork.
        """
        all_jobs = []
        queries = ["Data Analyst", "Data Engineer", "Business Analyst"]
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        search_location = location if location != "France" else country
        
        try:
            for query in queries:
                if progress_callback:
                    progress_callback(f"Recherche '{query}' à '{search_location}' sur HelloWork...")
                
                # Charger la page de recherche (d=3 pour les 3 derniers jours)
                search_url = f"{self.base_url}/fr-fr/emploi/recherche.html?k={query.replace(' ', '+')}&l={search_location.replace(' ', '+')}&d=3"
                logger.info(f"Navigating to {search_url}")
                
                try:
                    page.goto(search_url, wait_until="networkidle", timeout=60000)
                    # Petit délai pour le rendu dynamique
                    page.wait_for_timeout(2000)
                    
                    # Récupérer les offres
                    # Sélecteur identifié : li[data-id-storage-item-id]
                    cards = page.query_selector_all("li[data-id-storage-item-id]")
                    logger.info(f"Found {len(cards)} job cards for '{query}'")
                    
                    for card in cards:
                        try:
                            # Titre
                            title_el = card.query_selector("h3 p.tw-typo-l")
                            title = title_el.inner_text().strip() if title_el else "N/A"
                            
                            # Entreprise
                            company_el = card.query_selector("h3 p.tw-typo-s")
                            company = company_el.inner_text().strip() if company_el else "N/A"
                            
                            # URL
                            link_el = card.query_selector("a[data-cy='offerTitle']")
                            url = ""
                            if link_el:
                                href = link_el.get_attribute("href")
                                if href:
                                    url = self.base_url + href if href.startswith("/") else href
                            
                            # Localisation
                            loc_el = card.query_selector("div[data-cy='localisationCard']")
                            location = loc_el.inner_text().strip() if loc_el else "France"
                            
                            # Date
                            date_el = card.query_selector("div.tw-typo-s.tw-text-grey-500")
                            date_text = date_el.inner_text().strip() if date_el else ""
                            published_date = parse_relative_date(date_text)
                            
                            job_data = {
                                "job_title": title,
                                "company": company,
                                "location": location,
                                "published_date": published_date,
                                "url": url,
                                "source": self.source_name
                            }
                            
                            if url and title != "N/A":
                                all_jobs.append(job_data)
                                
                        except Exception as e:
                            logger.error(f"Error parsing HelloWork card: {e}")
                            continue
                            
                    # Pagination - on se limite à la première page pour la rapidité 
                    # puisque d=3 ramène déjà les plus récentes
                    
                except Exception as e:
                    logger.error(f"Error scraping {query} on HelloWork: {e}")
                    continue
                    
                # Délai aléatoire entre les requêtes
                time.sleep(random.uniform(2, 5))
                
        finally:
            context.close()
            
        return all_jobs
