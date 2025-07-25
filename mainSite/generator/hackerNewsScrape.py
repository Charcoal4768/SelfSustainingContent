import requests
import random
import json
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
# from . import grandparent_dir
current_script_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(current_script_path)
grandparent_dir = os.path.dirname(parent_dir)

load_dotenv(os.path.join(grandparent_dir, '.env'))

url = "https://uj5wyc0l7x-dsn.algolia.net/1/indexes/Item_dev_sort_date/query"

# url = "https://news.ycombinator.com/item?id=43512951"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

headers = {
    "User-Agent": random.choice(user_agents),
    "x-algolia-application-id": os.getenv("ALGOLIA_APP_ID"),
    "x-algolia-api-key": os.getenv("ALGOLIA_API_KEY"),
    "Content-Type": "application/json",
    "Referer": "https://hn.algolia.com/",
    "Origin": "https://hn.algolia.com"
}

data = {
    "query": "hostinger",
    "analyticsTags": ["web"],
    "page": 0,
    "hitsPerPage": 30,
    "minWordSizefor1Typo": 4,
    "minWordSizefor2Typos": 8,
    "advancedSyntax": True,
    "ignorePlurals": False,
    "clickAnalytics": True,
    "minProximity": 7,
    "numericFilters": [],
    "tagFilters": [["story"], []],
    "typoTolerance": True,
    "queryType": "prefixNone",
    "restrictSearchableAttributes": ["title", "comment_text", "story_text", "author"],
    "getRankingInfo": True
}

response = requests.post(url, json=data, headers=headers)

discussions = []

def search(amount, terms=[[None, None], [None, None]]):
    try:
        data = response.json()
        jsonified = json.dumps(data, indent=2)
        for hit in data.get("hits", []):
            url = hit.get('url', 'No URL')
            story_id = hit.get('story_id', 'No story ID')
            points = hit.get('points', 'No points')
            if points > 0 and story_id != 'No story ID':
                discussions.append({
                    "story_url": f"https://hn.algolia.com/item?id={story_id}",
                    "extra_url": url
                })
        print(f"Found {len(discussions)} discussions with points > 0")
    except Exception as e:
        print("Not JSON, content was:")
        print(response.text[:1000]) 
