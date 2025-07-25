import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    "Accept-Language": "en-US,en;q=0.9"
}

subreddit = ""
term = ""

url_sub = f"https://www.reddit.com/{subreddit}/search/?q={term}"
url_default = f"https://www.reddit.com/search/?q={term}"

response = requests.get(url_sub, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    post_links = soup.find_all("a", {"data-testid": "post-title-text"})
    
    for post in post_links:
        title = post.text.strip()
        href = post['href']
        print(f"{title}\nhttps://www.reddit.com{href}\n")

else:
    print(f"Failed to fetch page: {response.status_code}")
