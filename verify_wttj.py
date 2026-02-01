from scraper.sources.wttj_scraper import WTTJScraper
from playwright.sync_api import sync_playwright

def test_wttj():
    scraper = WTTJScraper()
    print("Testing WTTJ Scraper...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Search for something common
        scraper.search_queries = ["Data Analyst"] 
        
        try:
            jobs = scraper.scrape(browser, country="France", location="Paris")
            print(f"Found {len(jobs)} jobs.")
            if jobs:
                print("Sample job:", jobs[0])
            else:
                print("No jobs found. Possible selector issue.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    test_wttj()
