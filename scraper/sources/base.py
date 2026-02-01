"""
Interface de base pour les scrapers de sources d'offres d'emploi.
"""
import time
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Callable, Optional
from playwright.sync_api import Browser, Page
from config import MAX_RETRIES, RETRY_DELAY, REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, USER_AGENTS


class SourceScraper(ABC):
    """Classe abstraite pour les scrapers de sources."""
    
    def __init__(self, source_name: str):
        """
        Initialise le scraper.
        
        Args:
            source_name: Nom de la source (ex: "Indeed", "WTTJ")
        """
        self.source_name = source_name
    
    @abstractmethod
    def scrape(self, browser: Browser, country: str = "France", location: str = "France", queries: Optional[List[str]] = None, progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Scrappe les offres d'emploi de la source.
        
        Args:
            browser: Instance Playwright Browser
            country: Pays cible (ex: "France", "Belgique")
            location: Région ou ville cible
            progress_callback: Fonction de callback pour le progrès (optionnel)
        
        Returns:
            Liste de dictionnaires contenant les données des offres
        """
        pass
    
    def _get_random_user_agent(self) -> str:
        """Retourne un user agent aléatoire."""
        return random.choice(USER_AGENTS)
    
    def _random_delay(self):
        """Attend un délai aléatoire entre les requêtes."""
        delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        time.sleep(delay)
    
    def _retry_on_failure(self, func: Callable, max_retries: int = MAX_RETRIES) -> any:
        """
        Réessaie une fonction en cas d'échec.
        
        Args:
            func: Fonction à exécuter
            max_retries: Nombre maximum de tentatives
        
        Returns:
            Résultat de la fonction
        """
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(RETRY_DELAY * (attempt + 1))
        return None
    
    def _create_page(self, browser: Browser) -> Page:
        """
        Crée une nouvelle page avec configuration anti-détection.
        
        Args:
            browser: Instance Playwright Browser
        
        Returns:
            Page configurée
        """
        context = browser.new_context(
            user_agent=self._get_random_user_agent(),
            viewport={'width': 1920, 'height': 1080},
            locale='fr-FR'
        )
        page = context.new_page()
        return page
    
    def _safe_get_text(self, element, default: str = '') -> str:
        """
        Extrait le texte d'un élément de manière sécurisée.
        
        Args:
            element: Élément Playwright
            default: Valeur par défaut si erreur
        
        Returns:
            Texte de l'élément
        """
        try:
            return element.inner_text().strip() if element else default
        except Exception:
            return default
    
    def _safe_get_attribute(self, element, attr: str, default: str = '') -> str:
        """
        Extrait un attribut d'un élément de manière sécurisée.
        
        Args:
            element: Élément Playwright
            attr: Nom de l'attribut
            default: Valeur par défaut si erreur
        
        Returns:
            Valeur de l'attribut
        """
        try:
            return element.get_attribute(attr) or default
        except Exception:
            return default
    
    def _log_progress(self, message: str, progress_callback: Optional[Callable] = None):
        """
        Log un message de progrès.
        
        Args:
            message: Message à logger
            progress_callback: Fonction de callback
        """
        if progress_callback:
            progress_callback(f"[{self.source_name}] {message}")
        else:
            print(f"[{self.source_name}] {message}")
