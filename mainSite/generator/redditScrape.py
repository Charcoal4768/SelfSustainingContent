from flask import json
import requests
import random
import os
import time
from bs4 import BeautifulSoup
# from . import parent_dir

# current_script_path = os.path.abspath(__file__)
# parent_dir = os.path.dirname(current_script_path)

user_agents = [
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

headers = {
    'User-Agent': random.choice(user_agents),
    "Accept-Language": "en-US,en;q=0.9"
}

def subreddit_validator(subreddits):
    #check if subreddits in list are real by visiting them
    valid_subreddits = []
    for sub in subreddits:
        if sub is None or sub.strip() == "":
            continue
        print(f"Validating subreddit: {sub}")
        url = f"https://www.reddit.com/{sub}/"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # for invalid subreddits: page will load a div with class text-24 s:text-20, janky but works
            soup = BeautifulSoup(response.text, 'html.parser')
            if soup.find("div", class_="text-24 s:text-20"):
                print(f"Subreddit {sub} is invalid.")
            else:
                valid_subreddits.append(sub)
        else:
            print(f"Subreddit {sub} does not exist or is not accessible.")

    return valid_subreddits

def extract_comment(comments, current_depth=0, max_depth=3):
    hard_limit = 10 #we are not rich enough to afford processsing more ;-;
    extracted = []

    if len(extracted) >= hard_limit:
        return extracted

    for comment in comments:
        if comment.get("kind") != "t1":
            continue

        c_data = comment.get("data", {})
        c_score = c_data.get("score", 0)
        c_body = c_data.get("body", "")

        if c_score > 1 and len(c_body.strip()) > 20:
            extracted.append(c_body.strip())

        # Only recurse if we're still under depth
        if current_depth < max_depth:
            replies = c_data.get("replies")
            if replies and isinstance(replies, dict):
                nested_comments = replies.get("data", {}).get("children", [])
                extracted.extend(
                    extract_comment(
                        nested_comments,
                        current_depth=current_depth + 1,
                        max_depth=max_depth
                    )
                )

    return extracted

def extract_from_discussion(discussions):
    for discussion in discussions:
        urls = discussion["url"]
        for url in urls:
            url = url.rstrip("/") + ".json"
            response = requests.get(url, headers=headers)
            if not response.status_code == 200:
                print(f"Failed to fetch {url}")
                return None
            
            data = response.json()

            post_info = data[0]["data"]["children"][0]["data"]
            post_title = post_info["title"]
            # post_body = post_info["selftext"]

            comments_data = data[1]["data"]["children"]
            extracted_comments = extract_comment(comments_data)
            discussion["title"] = post_title
            # discussion["body"] = post_body
            discussion["comments"] = extracted_comments
        del discussion["url"]

    return discussions


def find_discussions(url,amount):
    discussions = []
    response = requests.get(url=url,headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text,'html.parser')

        post_links = soup.find_all("a",{"data-testid":"post-title-text"})

        for post in post_links:
            amount -= 1
            href = f"https://www.reddit.com{post['href']}"
            discussions.append(href)
            if amount == 0:
                break
    print(f"Found {len(discussions)} discussions on {url}")
    return discussions


def search(amount=2,terms=[[None,None],[None,None]],subreddits=[[None,None],[None,None]]):
    if not all(isinstance(group, list) for group in terms):
        raise ValueError("terms must be a list of lists (e.g., [['term1', 'term2'], ['term3']])")
    links_found = []
    if terms == [[None, None], [None, None]]:
        return links_found
    if amount <= 0:
        return links_found
    if subreddits == [[None, None], [None, None]] or not subreddits[0] or not subreddits[1]:
        base_url = "https://www.reddit.com/search/?q={}"
        for idx in range(2):
            for term in terms[idx]:
                url = base_url.format(term)
                time.sleep(0.5)
                links_found.append({"url":find_discussions(url, amount)})
    else:
        base_url = "https://www.reddit.com/{}/search/?q={}"
        for idx in range(2):  # 0 = product_1, 1 = product_2
            for subreddit in subreddits[idx]:
                for term in terms[idx]:
                    url = base_url.format(subreddit, term)
                    time.sleep(0.5)
                    links_found.append({"url":find_discussions(url, amount)})
    return links_found


if __name__ == "__main__":
    # Example search terms and subreddits
    links = search(2,[["Digital Ocean", "DO", "cloud hosting", "VPS"],["Hostinger", "web hosting", "shared hosting", "cheap hosting"]],[["r/digitalocean", "r/cloudcomputing", "r/selfhosted"],["r/webhosting", "r/hosting", "r/hostinger"]])

    for link in links:
        print(link)
        post = extract_from_discussion(link)
        #dump post into a file
        if post:
            #filename = first word of title
            #make sure there is no "/" in the filename
            post['title'] = post['title'].replace("/", "-")
            filename = post['title'].split()[0]
            with open(f"{filename}.json", "w+") as f:
                json.dump(post, f)