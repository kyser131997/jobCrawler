"""
Scraper pour APEC.
"""
import logging
import time
import random
from typing import List, Dict, Optional, Callable
from playwright.sync_api import Browser
from scraper.sources.base import SourceScraper
from scraper.utils import parse_relative_date

logger = logging.getLogger(__name__)

class APECScraper(SourceScraper):
    def __init__(self):
        super().__init__("APEC")
        self.base_url = "https://www.apec.fr"
        
    def scrape(self, browser: Browser, country: str = "France", location: str = "France", progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Scrape les offres de l'APEC.
        """
        all_jobs = []
        queries = ["Data Analyst", "Data Engineer"]
        
        if country.lower() != "france":
            if progress_callback:
                progress_callback("APEC est réservé à la France. Recherche ignorée.")
            return []

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            for query in queries:
                if progress_callback:
                    progress_callback(f"Recherche '{query}' à '{location}' sur APEC...")
                
                # URL de recherche APEC
                # lieux=596001 pour France entière, sinon on met le nom de la ville
                loc_param = "596001" if location.lower() == "france" else location.replace(' ', '%20')
                search_url = f"{self.base_url}/candidat/recherche-emploi.html/listeofr?motsCles={query.replace(' ', '%20')}&lieux={loc_param}&sort=DATE"
                logger.info(f"Navigating to {search_url}")
                
                try:
                    page.goto(search_url, wait_until="networkidle", timeout=60000)
                    
                    # Gérer le bandeau de cookies
                    try:
                        cookie_button = page.wait_for_selector("#didomi-notice-agree-button", timeout=5000)
                        if cookie_button:
                            cookie_button.click()
                            logger.info("APEC: Cookie consent accepted")
                            page.wait_for_timeout(2000)
                    except:
                        # Pas de bandeau ou déjà accepté
                        pass
                    
                    # Attendre que les résultats se chargent (APEC est lent)
                    try:
                        page.wait_for_selector(".container-resultat, .card-offer", timeout=20000)
                    except:
                        logger.warning(f"Timeout waiting for results on APEC for {query}")
                        # On tente quand même de scroller au cas où
                    
                    # Scroll progressif pour déclencher le chargement
                    for _ in range(3):
                        page.evaluate("window.scrollBy(0, 500)")
                        page.wait_for_timeout(1000)
                    
                    cards = page.query_selector_all(".container-resultat, .card-offer")
                    logger.info(f"Found {len(cards)} job cards for '{query}' on APEC")
                    
                    for card in cards:
                        try:
                            # Titre
                            title_el = card.query_selector(".card-title")
                            title = title_el.inner_text().strip() if title_el else "N/A"
                            
                            # Entreprise
                            company_el = card.query_selector(".card-offer__company")
                            company = company_el.inner_text().strip() if company_el else "N/A"
                            
                            # URL
                            url = ""
                            href_el = card.query_selector("a")
                            if href_el:
                                href = href_el.get_attribute("href")
                                if href:
                                    url = self.base_url + href if href.startswith("/") else href
                            
                            # Localisation
                            loc_el = card.query_selector(".card-offer__location, .card-offer__text")
                            location = loc_el.inner_text().strip() if loc_el else "France"
                            
                            # Date
                            date_el = card.query_selector(".card-offer__date")
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
                            logger.error(f"Error parsing APEC card: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error scraping {query} on APEC: {e}")
                    continue
                    
                time.sleep(random.uniform(3, 6))
                
        finally:
            context.close()
            
        return all_jobs
