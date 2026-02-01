"""
Données de géocodage statiques pour les principales villes cibles.
Permet d'afficher une carte sans dépendance à une API externe.
"""

CITY_COORDINATES = {
    # France
    "paris": (48.8566, 2.3522),
    "lyon": (45.7640, 4.8357),
    "marseille": (43.2965, 5.3698),
    "toulouse": (43.6047, 1.4442),
    "nice": (43.7102, 7.2620),
    "nantes": (47.2184, -1.5536),
    "strasbourg": (48.5734, 7.7521),
    "montpellier": (43.6108, 3.8767),
    "bordeaux": (44.8378, -0.5792),
    "lille": (50.6292, 3.0573),
    "rennes": (48.1173, -1.6778),
    "reims": (49.2583, 4.0317),
    "saint-etienne": (45.4397, 4.3872),
    "le havre": (49.4944, 0.1079),
    "toulon": (43.1242, 5.9280),
    "grenoble": (45.1885, 5.7245),
    "dijon": (47.3220, 5.0415),
    "angers": (47.4784, -0.5361),
    "nimes": (43.8367, 4.3601),
    "villeurbanne": (45.7719, 4.8783),
    "france": (46.2276, 2.2137),
    "ile-de-france": (48.8499, 2.6370),
    "idf": (48.8499, 2.6370),
    
    # Belgique
    "bruxelles": (50.8503, 4.3517),
    "brussels": (50.8503, 4.3517),
    "anvers": (51.2194, 4.4025),
    "antwerpen": (51.2194, 4.4025),
    "gand": (51.0543, 3.7174),
    "gent": (51.0543, 3.7174),
    "belgique": (50.5039, 4.4699),
    
    # Suisse
    "zurich": (47.3769, 8.5417),
    "geneve": (46.2044, 6.1432),
    "geneva": (46.2044, 6.1432),
    "lausanne": (46.5197, 6.6323),
    "bale": (47.5596, 7.5886),
    "basel": (47.5596, 7.5886),
    "suisse": (46.8182, 8.2275),
    
    # Luxembourg
    "luxembourg": (49.6116, 6.1319),
    
    # UK
    "london": (51.5074, -0.1278),
    "londres": (51.5074, -0.1278),
    "manchester": (53.4808, -2.2426),
    "birmingham": (52.4862, -1.8904),
    "united kingdom": (55.3781, -3.4360),
    
    # Espagne
    "madrid": (40.4168, -3.7038),
    "barcelona": (41.3851, 2.1734),
    "barcelone": (41.3851, 2.1734),
    "valencia": (39.4699, -0.3763),
    "valence": (39.4699, -0.3763),
    "espana": (40.4637, -3.7492),
    "espagne": (40.4637, -3.7492),
}

def get_coords(location_str: str) -> tuple[float, float]:
    """
    Tente de trouver les coordonnées pour une chaîne de localisation.
    """
    if not location_str:
        return None, None
        
    loc_lower = location_str.lower()
    
    # Recherche exacte
    if loc_lower in CITY_COORDINATES:
        return CITY_COORDINATES[loc_lower]
        
    # Recherche par sous-chaîne
    for city, coords in CITY_COORDINATES.items():
        if city in loc_lower:
            return coords
            
    return None, None
