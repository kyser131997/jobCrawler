"""
Scraper pour Glassdoor.
"""
import logging
import time
import random
from typing import List, Dict, Optional
from playwright.sync_api import Browser
from scraper.sources.base import SourceScraper
from scraper.utils import parse_relative_date

logger = logging.getLogger(__name__)

class GlassdoorScraper(SourceScraper):
    def __init__(self):
        super().__init__("Glassdoor")
        self.base_url = "https://www.glassdoor.fr"
        
    def scrape(self, browser: Browser, progress_callback=None) -> List[Dict]:
        """
        Scrape les offres de Glassdoor.
        """
        all_jobs = []
        # Glassdoor est très sensible, on limite les requêtes
        queries = ["Data Analyst"]
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            for query in queries:
                if progress_callback:
                    progress_callback(f"Recherche '{query}' sur Glassdoor...")
                
                # URL de recherche Glassdoor France
                # Note: Ces URLs peuvent expirer ou changer
                search_url = f"{self.base_url}/Emploi/france-{query.lower().replace(' ', '-')}-emplois-SRCH_IL.0,6_IN86_KO7,19.htm"
                logger.info(f"Navigating to {search_url}")
                
                try:
                    page.goto(search_url, wait_until="networkidle", timeout=60000)
                    
                    # Vérifier si on est bloqué
                    if "Aidez-nous à protéger Glassdoor" in page.content() or "Just a moment" in page.content():
                        logger.warning("Glassdoor anti-bot detected. Skipping for this run.")
                        if progress_callback:
                            progress_callback("⚠️ Glassdoor: Anti-bot détecté (Cloudflare). Tentative de contournement...")
                        
                        # Petite attente au cas où Turnstile se résout tout seul (rare)
                        page.wait_for_timeout(5000)
                        
                        if "Aidez-nous à protéger" in page.content():
                             continue

                    # Attendre les résultats
                    try:
                        page.wait_for_selector('[data-test="job-listing"]', timeout=10000)
                    except:
                        logger.warning(f"Timeout waiting for Glassdoor results for {query}")
                    
                    cards = page.query_selector_all('[data-test="job-listing"]')
                    logger.info(f"Found {len(cards)} job cards for '{query}' on Glassdoor")
                    
                    for card in cards:
                        try:
                            # Titre
                            title_el = card.query_selector('[data-test="job-title"]')
                            title = title_el.inner_text().strip() if title_el else "N/A"
                            
                            # Entreprise
                            company_el = card.query_selector('[data-test="employer-short-name"]')
                            company = company_el.inner_text().strip() if company_el else "N/A"
                            
                            # URL
                            url = ""
                            href_el = card.query_selector('[data-test="job-link"]')
                            if href_el:
                                href = href_el.get_attribute("href")
                                if href:
                                    url = self.base_url + href if href.startswith("/") else href
                            
                            # Localisation
                            loc_el = card.query_selector('[data-test="location"]')
                            location = loc_el.inner_text().strip() if loc_el else "France"
                            
                            # Date
                            date_el = card.query_selector('[data-test="listing-age"]')
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
                            logger.error(f"Error parsing Glassdoor card: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error scraping {query} on Glassdoor: {e}")
                    continue
                    
                time.sleep(random.uniform(4, 7))
                
        finally:
            context.close()
            
        return all_jobs
