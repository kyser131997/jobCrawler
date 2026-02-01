"""
Scraper pour Indeed France (indeed.fr).
"""
from typing import List, Dict, Optional, Callable
from playwright.sync_api import Browser, TimeoutError as PlaywrightTimeout
from scraper.sources.base import SourceScraper
from scraper.utils import parse_relative_date, clean_text, extract_snippet, normalize_url


class IndeedScraper(SourceScraper):
    """Scraper pour Indeed France."""
    
    def __init__(self):
        super().__init__("Indeed")
        self.base_url = "https://fr.indeed.com"
        self.search_queries = [
            "Data Analyst",
            "Business Analyst",
            "Data Engineer",
            "Ingénieur Data"
        ]
    
    def scrape(self, browser: Browser, country: str = "France", location: str = "France", queries: Optional[List[str]] = None, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """Scrappe les offres d'Indeed."""
        all_jobs = []
        
        # Utiliser les requêtes fournies ou celles par défaut
        queries_to_use = queries if queries else self.search_queries
        
        # Ajuster l'URL de base selon le pays
        if country.lower() == "france":
            self.base_url = "https://fr.indeed.com"
        elif country.lower() == "belgique":
            self.base_url = "https://be.indeed.com"
        elif country.lower() == "suisse":
            self.base_url = "https://ch.indeed.com"
        else:
            self.base_url = "https://www.indeed.com"
            
        for query in queries_to_use:
            self._log_progress(f"Recherche: {query} à {location} ({country})", progress_callback)
            
            try:
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
            # Construire l'URL de recherche
            search_url = f"{self.base_url}/jobs?q={query.replace(' ', '+')}&l={location.replace(' ', '+')}&fromage=3"
            
            self._log_progress(f"Chargement: {search_url}", progress_callback)
            page.goto(search_url, wait_until='domcontentloaded', timeout=40000)
            
            # Petit délai pour laisser le temps au contenu de s'afficher (anti-bot)
            page.wait_for_timeout(3000)
            
            # Attendre que les résultats se chargent
            try:
                page.wait_for_selector('.job_seen_beacon, .jobsearch-ResultsList, #mosaic-provider-jobcards', timeout=15000)
            except PlaywrightTimeout:
                # Vérifier si on est bloqué
                if "hCaptcha" in page.content() or "Cloudflare" in page.content() or "Verify you are human" in page.content():
                    self._log_progress("Accès bloqué par un Captcha/Cloudflare", progress_callback)
                else:
                    self._log_progress("Aucun résultat trouvé (Timeout)", progress_callback)
                return jobs
            
            # Extraire les offres
            job_cards = page.query_selector_all('.job_seen_beacon, .jobCard')
            self._log_progress(f"{len(job_cards)} offres sur la page", progress_callback)
            
            for card in job_cards[:20]:  # Limiter à 20 offres par requête
                try:
                    job_data = self._extract_job_from_card(card, page)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
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
            title_elem = card.query_selector('h2.jobTitle, .jobTitle span')
            title = self._safe_get_text(title_elem)
            if not title:
                return None
            
            # Entreprise
            company_elem = card.query_selector('[data-testid="company-name"], .companyName')
            company = self._safe_get_text(company_elem, 'Non spécifié')
            
            # Localisation
            location_elem = card.query_selector('[data-testid="text-location"], .companyLocation')
            location = self._safe_get_text(location_elem, 'France')
            
            # Date (Indeed change souvent de structure)
            date_text = ""
            date_selectors = [
                'span.date',
                'span[class*="date"]',
                '.date',
                '[data-testid="myJobsStateDate"]',
                '.jobsearch-JobMetadataFooter span',
                'span[class*="Metadata"]',
                '.css-qv629i' # Common Indeed class for metadata
            ]
            
            for selector in date_selectors:
                date_elem = card.query_selector(selector)
                if date_elem:
                    cand_text = self._safe_get_text(date_elem)
                    # Vérifier si c'est vraiment une date (contient des mots clés temporels)
                    if cand_text and any(k in cand_text.lower() for k in ['il y a', 'publié', 'posted', 'day', 'jour', 'h', 'min', 'instant', 'hier', 'today', 'ajourd', 'active', 'nouvelle', 'maintenant', 'semaine']):
                        date_text = cand_text
                        # print(f"DEBUG Indeed: Trouvé via {selector}: {date_text}")
                        break
            
            # Fallback par recherche textuelle encore plus large
            if not date_text:
                try:
                    # On cherche dans tous les éléments descendants qui pourraient contenir du texte
                    date_text = card.evaluate("""(node) => {
                        const elements = node.querySelectorAll('span, div, p');
                        const dateKeywords = ['il y a', 'publié', 'posted', 'active', 'nouvelle', 'jour', 'hour', 'heure', 'maintenant', 'instant', 'hier', 'today', 'week', 'semaine', 'ago'];
                        
                        for (const el of elements) {
                            const txt = el.innerText.trim();
                            const txtLower = txt.toLowerCase();
                            if (dateKeywords.some(k => txtLower.includes(k))) {
                                // On évite les textes trop longs qui pourraient être des descriptions
                                if (txt.length > 1 && txt.length < 60) {
                                    return txt;
                                }
                            }
                        }
                        return '';
                    }""")
                    if date_text:
                        print(f"DEBUG Indeed: Trouvé via fallback JS: {date_text}")
                except Exception:
                    pass
            
            if not date_text:
                 print(f"DEBUG Indeed: Date NON TROUVÉE pour {job_title}")
                        
            published_date = parse_relative_date(date_text) if date_text else None
            
            # Debug log if we still don't have a date but we have text in the card
            if not published_date and not date_text:
                # Tentative ultime : prendre tout le texte et chercher un motif type "X jours"
                all_card_text = self._safe_get_text(card).lower()
                match = re.search(r'(publi[\w\sèé]+|il y a|posted)\s*[:]?\s*(\d+|\+)?\s*(jour|hour|heure|semaine|week|month|mois|day|j|h|d|w|m|s)', all_card_text)
                if match:
                    date_text = match.group(0)
                    published_date = parse_relative_date(date_text)
            
            # URL
            link_elem = card.query_selector('a[data-jk], h2.jobTitle a')
            url = ''
            if link_elem:
                href = self._safe_get_attribute(link_elem, 'href')
                if href:
                    url = normalize_url(f"{self.base_url}{href}" if href.startswith('/') else href)
            
            # Snippet (description courte)
            snippet_elem = card.query_selector('.job-snippet, [data-testid="job-snippet"]')
            snippet = extract_snippet(self._safe_get_text(snippet_elem))
            
            return {
                'job_title': clean_text(title),
                'company': clean_text(company),
                'location': clean_text(location),
                'published_date': published_date,
                'url': url,
                'snippet': snippet,
                'source': self.source_name
            }
        
        except Exception as e:
            return None
