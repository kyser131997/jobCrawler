"""
Fonctions utilitaires pour le scraping et le traitement des données.
"""
import re
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Set
from dateutil import parser as date_parser
from config import MAX_DAYS_OLD, FRENCH_LOCATIONS, ROLE_CATEGORIES, KEYWORDS


def is_recent(date_str: str, max_days: int = MAX_DAYS_OLD) -> bool:
    """
    Vérifie si une date est récente (≤ max_days jours).
    
    Args:
        date_str: Date sous forme de string (ISO ou format libre)
        max_days: Nombre maximum de jours
    
    Returns:
        True si la date est récente
    """
    if not date_str:
        return False
    
    try:
        # Parser la date
        if isinstance(date_str, datetime):
            pub_date = date_str
        else:
            pub_date = date_parser.parse(date_str, fuzzy=True)
        
        # Comparer avec aujourd'hui
        cutoff_date = datetime.now() - timedelta(days=max_days)
        return pub_date >= cutoff_date
    except Exception:
        return False


def is_valid_location(location: str, target_location: str = "France") -> bool:
    """
    Vérifie si une localisation correspond à la cible ou est acceptable.
    
    Args:
        location: Localisation de l'offre (ville, région, etc.)
        target_location: Localisation cible choisie par l'utilisateur
    
    Returns:
        True si la localisation est valide
    """
    if not location or target_location.lower() == "france":
        return True # On accepte tout si France ou non spécifié (le scraper a déjà filtré en amont)
    
    location_lower = location.lower()
    target_lower = target_location.lower()
    
    # Si le mot-clé de la cible est dans la localisation de l'offre
    if target_lower in location_lower:
        return True
        
    return True # Par défaut on est indulgent pour ne pas rater d'offres
    if any(k in location_lower for k in ['france', 'remote', 'télétravail', 'distanciel', 'idf', 'île-de-france']):
        return True

    # Vérifier si contient un mot-clé français spécifique
    for french_loc in FRENCH_LOCATIONS:
        if french_loc in location_lower:
            return True
    
    return False


def detect_keywords(text: str) -> Set[str]:
    """
    Détecte les mots-clés dans un texte.
    
    Args:
        text: Texte à analyser (titre + description)
    
    Returns:
        Set de mots-clés détectés
    """
    if not text:
        return set()
    
    text_lower = text.lower()
    detected = set()
    
    # Vérifier tous les mots-clés
    for category, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected.add(keyword)
    
    return detected


def matches_keywords(text: str) -> bool:
    """
    Vérifie si un texte contient au moins un mot-clé pertinent.
    
    Args:
        text: Texte à analyser
    
    Returns:
        True si au moins un mot-clé est trouvé
    """
    return len(detect_keywords(text)) > 0


def categorize_role(text: str) -> str:
    """
    Catégorise le rôle en fonction du texte (titre + description).
    
    Ordre de priorité:
    1. Data Engineer
    2. Data Analyst
    3. Business Analyst
    4. Other (si contient "data" ou "business")
    
    Args:
        text: Texte à analyser
    
    Returns:
        Catégorie du rôle
    """
    if not text:
        return 'Other'
    
    text_lower = text.lower()
    
    # Vérifier dans l'ordre de priorité
    for category, keywords in ROLE_CATEGORIES.items():
        if category == 'Other':
            continue
        for keyword in keywords:
            if keyword in text_lower:
                return category
    
    # Fallback: Other si contient "data" ou "business"
    if 'data' in text_lower or 'business' in text_lower or 'données' in text_lower:
        return 'Other'
    
    return 'Other'


def clean_text(text: str) -> str:
    """
    Nettoie un texte (supprime espaces multiples, retours à la ligne, etc.).
    
    Args:
        text: Texte à nettoyer
    
    Returns:
        Texte nettoyé
    """
    if not text:
        return ''
    
    # Supprimer les retours à la ligne multiples
    text = re.sub(r'\n+', ' ', text)
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    # Trim
    text = text.strip()
    
    return text


def generate_hash(title: str, company: str, date: str) -> str:
    """
    Génère un hash unique pour une offre (utilisé si pas d'URL).
    
    Args:
        title: Titre de l'offre
        company: Entreprise
        date: Date de publication
    
    Returns:
        Hash MD5
    """
    content = f"{title}|{company}|{date}"
    return hashlib.md5(content.encode()).hexdigest()


def extract_snippet(description: str, max_length: int = 300) -> str:
    """
    Extrait un snippet (résumé court) d'une description.
    
    Args:
        description: Description complète
        max_length: Longueur maximale du snippet
    
    Returns:
        Snippet
    """
    if not description:
        return ''
    
    cleaned = clean_text(description)
    
    if len(cleaned) <= max_length:
        return cleaned
    
    # Couper au dernier espace avant max_length
    snippet = cleaned[:max_length]
    last_space = snippet.rfind(' ')
    if last_space > 0:
        snippet = snippet[:last_space]
    
    return snippet + '...'


def normalize_url(url: str) -> str:
    """
    Normalise une URL (supprime les paramètres de tracking, etc.).
    
    Args:
        url: URL brute
    
    Returns:
        URL normalisée
    """
    if not url:
        return ''
    
    # Supprimer les paramètres de tracking courants
    url = re.sub(r'[?&](utm_|ref=|source=)[^&]*', '', url)
    # Supprimer le ? final si vide
    url = re.sub(r'\?$', '', url)
    
    return url.strip()


def parse_relative_date(date_text: str) -> Optional[datetime]:
    """
    Parse les dates relatives (ex: "il y a 2 jours", "2 days ago", "aujourd'hui").
    """
    if not date_text:
        return None
    
    date_text_lower = date_text.lower()
    now = datetime.now()
    
    # À l'instant / Just now / Maintenant
    if any(k in date_text_lower for k in ["instant", "maintenant", "now", "juste", "moment"]):
        return now
        
    # Aujourd'hui / today
    if 'aujourd\'hui' in date_text_lower or 'today' in date_text_lower or 'nouvelle' in date_text_lower:
        return now
    
    # Hier / yesterday
    if 'hier' in date_text_lower or 'yesterday' in date_text_lower:
        return now - timedelta(days=1)
    
    # Il y a X jours / X days ago / X j / X d
    # On cherche un chiffre suivi de j, d, jour, day
    match = re.search(r'(\d+)\s*(jour|day|j|d)', date_text_lower)
    if match:
        days = int(match.group(1))
        return now - timedelta(days=days)
    
    # Il y a X heures / X hours ago / X h
    match = re.search(r'(\d+)\s*(heure|hour|h)', date_text_lower)
    if match:
        hours = int(match.group(1))
        return now - timedelta(hours=hours)
        
    # Il y a X semaines / X weeks ago / X w / X s
    match = re.search(r'(\d+)\s*(semaine|week|w|s)', date_text_lower)
    if match:
        weeks = int(match.group(1))
        return now - timedelta(weeks=weeks)
    
    # Essayer de parser normalement avec dateutil
    try:
        return date_parser.parse(date_text, fuzzy=True)
    except Exception:
        return None
