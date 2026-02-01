"""
Script de vérification du pipeline complet.
"""
import logging
import sys
import asyncio
from scraper.pipeline import ScrapingPipeline

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def test_pipeline():
    print("🧪 Démarrage du test du pipeline...")
    
    # Correction Windows pour asyncio
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    pipeline = ScrapingPipeline()
    
    def progress_handler(msg):
        print(f"  [PROGRÈS] {msg}")
    
    try:
        stats = pipeline.run(progress_callback=progress_handler)
        print("\n✅ Test terminé avec succès!")
        print(f"📊 Statistiques: {stats}")
    except Exception as e:
        print(f"\n❌ Erreur pendant le test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pipeline()
