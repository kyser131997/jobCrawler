import requests
import json

app_id = "CSEKHVMS53"
api_key = "4bd8f6215d0cc52b26430765769e65a0"

indices_to_try = [
    "wttj_jobs_production_fr_published_at_desc", 
    "wttj_jobs_production",
    "wttj_jobs_production_fr"
]

headers = {
    "X-Algolia-Application-Id": app_id,
    "X-Algolia-API-Key": api_key,
    "Content-Type": "application/json",
    "Referer": "https://www.welcometothejungle.com/"
}

for index_name in indices_to_try:
    url = f"https://{app_id.lower()}-dsn.algolia.net/1/indexes/{index_name}/query"
    data = {"params": "query=data analyst&hitsPerPage=2"}
    
    try:
        print(f"Testing index: {index_name}")
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("SUCCESS!")
            result = response.json()
            # Save to file
            with open("wttj_api_result.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            print("Saved result to wttj_api_result.json")
            break
        else:
            print(f"Failed with {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
