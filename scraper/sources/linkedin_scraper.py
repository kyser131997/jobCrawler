"""
Scraper pour LinkedIn Jobs (linkedin.com/jobs).
Note: LinkedIn peut nécessiter une authentification. Ce scraper fonctionne en mode public.
"""
from typing import List, Dict, Optional, Callable
from playwright.sync_api import Browser, TimeoutError as PlaywrightTimeout
from scraper.sources.base import SourceScraper
from scraper.utils import parse_relative_date, clean_text, extract_snippet, normalize_url


class LinkedInScraper(SourceScraper):
    """Scraper pour LinkedIn Jobs (mode public)."""
    
    def __init__(self):
        super().__init__("LinkedIn")
        self.base_url = "https://www.linkedin.com"
        self.search_queries = [
            "Data Analyst",
            "Business Analyst",
            "Data Engineer"
        ]
    
    def scrape(self, browser: Browser, country: str = "France", location: str = "France", queries: Optional[List[str]] = None, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Scrappe les offres de LinkedIn."""
        all_jobs = []
        
        # Utiliser les requêtes fournies ou celles par défaut
        queries_to_use = queries if queries else self.search_queries
        
        for query in queries_to_use:
            self._log_progress(f"Recherche: {query} à {location} ({country})", progress_callback)
            
            try:
                # Pour LinkedIn, on combine pays et région pour le paramètre location de l'URL
                # On utilise 'location' directement pour la recherche, car LinkedIn gère bien les noms de villes/pays
                jobs = self._scrape_query(browser, query, location, progress_callback)
                all_jobs.extend(jobs)
                self._random_delay()
            except Exception as e:
                self._log_progress(f"Erreur pour '{query}': {str(e)}", progress_callback)
                continue
        
        self._log_progress(f"Total: {len(all_jobs)} offres trouvées", progress_callback)
        return all_jobs
    
    def _scrape_query(self, browser: Browser, query: str, location: str, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Scrappe une requête de recherche spécifique."""
        jobs = []
        page = self._create_page(browser)
        
        try:
            # URL de recherche pour LinkedIn
            search_url = f"{self.base_url}/jobs/search?keywords={query.replace(' ', '%20')}&location={location.replace(' ', '%20')}&f_TPR=r259200"
            
            self._log_progress(f"Chargement: {search_url}", progress_callback)
            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            
            # Attendre le chargement
            try:
                page.wait_for_selector('.jobs-search__results-list, .job-search-card', timeout=10000)
            except PlaywrightTimeout:
                self._log_progress("Aucun résultat ou accès bloqué", progress_callback)
                return jobs
            
            # Scroll pour charger plus d'offres
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
            except Exception:
                pass
            
            # Extraire les offres
            job_cards = page.query_selector_all('.job-search-card, .base-card')
            self._log_progress(f"{len(job_cards)} offres sur la page", progress_callback)
            
            for card in job_cards[:15]:  # Limiter à 15 offres
                try:
                    job_data = self._extract_job_from_card(card, page)
                    if job_data:
                        jobs.append(job_data)
                except Exception:
                    continue
            
        except Exception as e:
            self._log_progress(f"Erreur lors du scraping: {str(e)}", progress_callback)
        finally:
            page.close()
        
        return jobs
    
    def _extract_job_from_card(self, card, page) -> Optional[Dict]:
        """Extrait les données d'une carte d'offre."""
        try:
            # Titre
            title_elem = card.query_selector('.base-search-card__title, h3')
            title = self._safe_get_text(title_elem)
            if not title:
                return None
            
            # Entreprise
            company_elem = card.query_selector('.base-search-card__subtitle, h4, .job-search-card__company-name')
            company = self._safe_get_text(company_elem, 'Non spécifié')
            
            # Localisation
            location_elem = card.query_selector('.job-search-card__location, .base-search-card__metadata')
            location = self._safe_get_text(location_elem, 'France')
            
            # URL
            link_elem = card.query_selector('a.base-card__full-link')
            url = ''
            if link_elem:
                href = self._safe_get_attribute(link_elem, 'href')
                if href:
                    # Nettoyer l'URL LinkedIn (supprimer les paramètres de tracking)
                    url = normalize_url(href.split('?')[0] if '?' in href else href)
            
            # Date
            date_elem = card.query_selector('time, .job-search-card__listdate')
            date_text = self._safe_get_text(date_elem)
            if not date_text:
                date_attr = self._safe_get_attribute(date_elem, 'datetime') if date_elem else ''
                date_text = date_attr
            published_date = parse_relative_date(date_text) if date_text else None
            
            # Snippet (LinkedIn n'affiche pas toujours de description dans les cartes)
            snippet = ''
            
            return {
                'job_title': clean_text(title),
                'company': clean_text(company),
                'location': clean_text(location),
                'published_date': published_date,
                'url': url,
                'snippet': snippet,
                'source': self.source_name
            }
        
        except Exception:
            return None
