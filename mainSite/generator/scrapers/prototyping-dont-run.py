import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
}

url = "https://www.reddit.com/r/Windows11/search/?q=rainmeter&cId=b546d9a4-32d9-4c42-89fe-d79eb3c4230b&iId=c53d6421-24a3-4e4f-87ee-17063e939ce0"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    post_links = soup.find_all("a", {"data-testid": "post-title-text"})
    
    for post in post_links:
        title = post.text.strip()
        href = post['href']
        print(f"{title}\nhttps://www.reddit.com{href}\n")

else:
    print(f"Failed to fetch page: {response.status_code}")
