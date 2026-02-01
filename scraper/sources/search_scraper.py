"""
Scraper basé sur la recherche (Meta-Search).
Utilise DuckDuckGo pour trouver des offres sur des sites d'ATS (Greenhouse, Lever, etc.).
"""
import logging
import time
import random
import urllib.parse
from typing import List, Dict, Optional
from playwright.sync_api import Browser
from scraper.sources.base import SourceScraper
from scraper.utils import parse_relative_date

logger = logging.getLogger(__name__)

class SearchScraper(SourceScraper):
    def __init__(self):
        super().__init__("Internet Search")
        # Utilisation de la version standard (plus discrète si on simule bien)
        self.base_url = "https://duckduckgo.com"
        
    def scrape(self, browser: Browser, progress_callback=None) -> List[Dict]:
        """
        Scrape les résultats de recherche pour trouver des offres.
        """
        all_jobs = []
        queries = [
            'site:greenhouse.io "Data Analyst" France',
            'site:lever.co "Data Analyst" France'
        ]
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        try:
            for query in queries:
                if progress_callback:
                    progress_callback(f"Meta-recherche: '{query}'...")
                
                try:
                    # Navigation vers la home d'abord pour paraître humain
                    page.goto(self.base_url, wait_until="networkidle")
                    page.wait_for_timeout(1000)
                    
                    # Taper la recherche
                    search_input = page.wait_for_selector("input[name='q']", timeout=10000)
                    search_input.fill(query)
                    page.keyboard.press("Enter")
                    
                    # Attendre les résultats
                    try:
                        page.wait_for_selector("article[data-testid='result'], .result", timeout=15000)
                        page.wait_for_timeout(2000)
                    except:
                        logger.warning(f"No search results found for {query}")
                        continue
                    
                    results = page.query_selector_all("article[data-testid='result'], .result")
                    logger.info(f"Found {len(results)} search results for '{query}'")
                    
                    for res in results:
                        try:
                            # Sélecteurs pour DDG standard
                            title_el = res.query_selector("h2 a span, .result__title")
                            title_text = title_el.inner_text().strip() if title_el else "N/A"
                            
                            # URL
                            url_el = res.query_selector("h2 a, .result__a")
                            url = url_el.get_attribute("href") if url_el else ""
                            
                            # Snippet
                            snippet_el = res.query_selector("div[data-testid='result-snippet'], .result__snippet")
                            snippet = snippet_el.inner_text().strip() if snippet_el else ""
                            
                            # Extraire l'entreprise si possible du titre
                            # Souvent: "Job Title at Company" ou "Company - Job Title"
                            company = "N/A"
                            if " at " in title_text:
                                parts = title_text.split(" at ")
                                title = parts[0].strip()
                                company = parts[1].split("|")[0].strip()
                            elif " - " in title_text:
                                parts = title_text.split(" - ")
                                # On devine lequel est l'entreprise
                                if len(parts) >= 2:
                                    company = parts[0].strip() if len(parts[0]) < len(parts[1]) else parts[1].strip()
                                    title = parts[1].strip() if len(parts[0]) < len(parts[1]) else parts[0].strip()
                            else:
                                title = title_text
                            
                            job_data = {
                                "job_title": title,
                                "company": company,
                                "location": "France (via web search)",
                                "published_date": parse_relative_date("today"),
                                "url": url,
                                "source": self.source_name,
                                "snippet": snippet
                            }
                            
                            if url and title != "N/A":
                                all_jobs.append(job_data)
                                
                        except Exception as e:
                            logger.error(f"Error parsing search result: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error searching {query}: {e}")
                    continue
                    
                # Pause pour éviter d'être bloqué par DDG
                time.sleep(random.uniform(5, 10))
                
        finally:
            context.close()
            
        return all_jobs
