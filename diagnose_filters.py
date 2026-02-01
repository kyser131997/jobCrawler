from scraper.pipeline import ScrapingPipeline
from scraper.sources.indeed_scraper import IndeedScraper
from scraper.sources.wttj_scraper import WTTJScraper
from scraper.sources.linkedin_scraper import LinkedInScraper
from scraper.sources.hellowork_scraper import HelloWorkScraper
from scraper.sources.apec_scraper import APECScraper
from scraper.sources.glassdoor_scraper import GlassdoorScraper
from scraper.sources.search_scraper import SearchScraper
from playwright.sync_api import sync_playwright
import logging

logging.basicConfig(level=logging.INFO)

def diagnose():
    pipeline = ScrapingPipeline()
    scrapers = [
        IndeedScraper(),
        WTTJScraper(),
        LinkedInScraper(),
        HelloWorkScraper(),
        APECScraper(),
        GlassdoorScraper(),
        SearchScraper()
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for scraper in scrapers:
            print(f"--- Diagnosing {scraper.source_name} ---")
            try:
                raw_jobs = scraper.scrape(browser)
                print(f"Raw jobs found: {len(raw_jobs)}")
                
                if len(raw_jobs) > 0:
                    print(f"Sample raw job: {raw_jobs[0]}")
                
                filtered = pipeline._filter_and_enrich(raw_jobs)
                print(f"Filtered jobs: {len(filtered)}")
                
                if len(raw_jobs) > 0 and len(filtered) == 0:
                    print("Reason for filtering first raw job:")
                    job = raw_jobs[0]
                    from scraper.utils import is_recent, is_valid_location, matches_keywords
                    print(f"  - is_recent: {is_recent(job.get('published_date')) if job.get('published_date') else 'N/A'}")
                    print(f"  - is_valid_location: {is_valid_location(job.get('location', ''))}")
                    text = f"{job.get('job_title', '')} {job.get('snippet', '')}"
                    print(f"  - matches_keywords: {matches_keywords(text)}")
                    print(f"  - location: '{job.get('location', '')}'")
                    print(f"  - text used for keywords: '{text}'")
            except Exception as e:
                print(f"Error: {e}")
            print("\n")
            
        browser.close()

if __name__ == "__main__":
    diagnose()
