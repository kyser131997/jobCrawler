import requests
import json

app_id = "CSEKHVMS53"
api_key = "4bd8f6215d0cc52b26430765769e65a0"
index_name = "wttj_jobs_production_fr_published_at_desc"

headers = {
    "X-Algolia-Application-Id": app_id,
    "X-Algolia-API-Key": api_key,
    "Content-Type": "application/json",
    "Referer": "https://www.welcometothejungle.com/"
}

# Test 1: Search for Bruxelles in the default FR index
url = f"https://{app_id.lower()}-dsn.algolia.net/1/indexes/{index_name}/query"
data = {
    "params": "query=data&facetFilters=[[\"offices.country_code:BE\"]]"
}

try:
    print(f"Testing Belgium (BE) in index: {index_name}")
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"Found {result['nbHits']} jobs.")
        if result['hits']:
            print("Sample job location:", result['hits'][0]['offices'][0]['city'], result['hits'][0]['offices'][0]['country_code'])
    else:
        print(f"Failed with {response.status_code}: {response.text}")

except Exception as e:
    print(f"Error: {e}")
