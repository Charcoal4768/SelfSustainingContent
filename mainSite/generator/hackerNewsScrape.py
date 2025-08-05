import requests
import random
import json
import os
import time
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

header1 = {
    "User-Agent": random.choice(user_agents),
    "x-algolia-application-id": os.getenv("ALGOLIA_APP_ID"),
    "x-algolia-api-key": os.getenv("ALGOLIA_API_KEY"),
    "Content-Type": "application/json",
    "Referer": "https://hn.algolia.com/",
    "Origin": "https://hn.algolia.com"
}

header2 = {
    "User-Agent": random.choice(user_agents),
    "cache-control": "private; max-age=0",
    "content-encoding": "gzip",
    "content-security-policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/ https://cdnjs.cloudflare.com/; frame-src 'self' https://www.google.com/recaptcha/; style-src 'self' 'unsafe-inline'; img-src 'self' https://account.ycombinator.com; frame-ancestors 'self'",
    "content-type": "text/html; charset=utf-8",
    "date": time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()),
    "referrer-policy": "origin",
    "server": "nginx",
    "vary": "Accept-Encoding"
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

def extract_from_discussion(links):
    print(links)
    for link in links:
        discussion = link["story_url"]
        link["comments"] = []
        response = requests.get(discussion, headers=header2)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            post_title = soup.find("div", class_="toptext").get_text(strip=True)
            comments = soup.find_all("div", class_="commtext")
            for comment in comments:
                comment_text = comment.get_text(strip=True)
                if comment_text and len(comment_text) > 10:  # filter out short comments
                    link["comments"].append(comment_text)
        del link["story_url"]
        time.sleep(0.5)
    return links

def search(amount, terms=[[None, None], [None, None]]):
    links = []
    if not terms or terms == [[None, None], [None, None]]:
        return links
    for term in terms:
        time.sleep(0.5)
        try:
            print(f"Searching HackerNews for term: {term[0]}")
            data["query"] = term[0] if term[0] else ""
            response = requests.post(url, headers=header1, json=data)
            if response.status_code != 200:
                print(f"Error: {response.status_code} for term {term[0]}")
                continue
            extracted = response.json()
            jsonified = json.dumps(extracted, indent=2)
            for hit in extracted.get("hits", []):
                story_id = hit.get('story_id', 'No story ID')
                points = hit.get('points', 'No points')
                if points > 0 and story_id != 'No story ID':
                    links.append({
                        "story_url": f"https://news.ycombinator.com/item?id={story_id}",
                        "title": hit.get('title', 'No title')
                    })
        except Exception as e:
            print("Not JSON, content was:")
            print(response.text[:1000]) 

    return links
