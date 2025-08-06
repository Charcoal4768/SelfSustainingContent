import os
import json
import time
import traceback
import threading
from threading import Event
from dotenv import load_dotenv

from . import (
    grandparent_dir, hackerNewsScrape, redditScrape,
    SentimentAnalysisPrompt, ArticlePrompt, TitlePrompt, SearchTermsPrompt,
    sendRequest
)
from mainSite.sockets import socketio

load_dotenv(os.path.join(grandparent_dir, '.env'))

def formatTerms(terms, progress_status):
    searchTerms1 = terms.get("SearchTerms1", [])
    searchTerms2 = terms.get("SearchTerms2", [])
    subreddit1 = terms.get("Subreddit1", [])
    subreddit2 = terms.get("Subreddit2", [])

    if not searchTerms1 or not searchTerms2:
        raise ValueError("Search terms cannot be empty")
    progress_status["status"] = "Validating subreddits..."
    subreddit1 = redditScrape.subreddit_validator(subreddit1) if subreddit1 else []
    subreddit2 = redditScrape.subreddit_validator(subreddit2) if subreddit2 else []

    return [searchTerms1, searchTerms2], [subreddit1, subreddit2]

def obtainTerms(product1,product2,Prompt,progress_status: dict[str,any]):
    progress_status["status"] = "Generating search terms..."
    response_text = sendRequest(prompt=Prompt)
    searchTerms = formatTerms(response_text,progress_status=progress_status)
    print(f"Search terms obtained: {searchTerms}")
    return searchTerms

def reddit_scrape(searchTerms, posts_container, progress_status: dict[str,any]):
    progress_status["status"] = "Searching Reddit..."
    links = redditScrape.search(2, searchTerms[0], searchTerms[1])
    progress_status["status"] = "Extracting comments from Reddit..."
    posts_container.extend(redditScrape.extract_from_discussion(links))

def hacker_news_scrape(searchTerms, posts_container, progress_status: dict[str,any]):
    progress_status["status"] = "Searching Hacker News..."
    links = hackerNewsScrape.search(2, searchTerms[0])
    progress_status["status"] = "Extracting comments from Hacker News..."
    posts_container.extend(hackerNewsScrape.extract_from_discussion(links))

def status_watcher(status_dict: dict[str,any], stop_event):
    from mainSite import socketio
    last_seen = None
    while not stop_event.is_set():
        current = status_dict["status"]
        if current != last_seen:
            last_seen = current
            socketio.emit("status_update", status_dict)
        time.sleep(0.5)
    
def article_emitter(article_data_structure: dict[str, any], title: dict[str, str]):
    # lines = []
    # intro = article_data_structure.get("Intro", "").strip()
    # if intro:
    #     lines.append(intro)
    #     lines.append("")

    # sections = article_data_structure.get("Sections", [])
    # for section in sections:
    #     heading = section.get("heading", "").strip()
    #     content = section.get("content", "").strip()
    #     if heading:
    #         lines.append(f"## {heading}")
    #     if content:
    #         lines.append(content)
    #     lines.append("")

    # full_article_text = "\n".join(lines).strip()
    final_title = title.get("Title", "").strip()
    description = title.get("Description","").strip()
    # tags = article_data_structure.get("Tags", [])

    # print(f"\n--- Final Article Content ---\n{full_article_text}\n")
    # print(f"Title: {final_title}")
    # print(f"Tags: {tags}")

    # to_emit = {
    #     "title": final_title,
    #     "tags": tags,
    #     "content": full_article_text
    # }
    to_emit = {"title":final_title,"content":article_data_structure,"description":description}

    socketio.emit("article_ready", to_emit)

def startProcess(Prompt: SearchTermsPrompt, article_extra_info: str, include_hacker_news: bool =False, article_type="Listicle"):
    progress_status = {
        "status": "idle",
        "last": None
    }
    posts = []
    progress_status["status"] = "idle"
    stop_event = threading.Event()

    watcher_thread = threading.Thread(
        target=status_watcher, 
        args=(progress_status, stop_event),
        daemon=True
    )
    watcher_thread.start()
    try:
        product1 = Prompt.product1
        product2 = Prompt.product2
        searchTerms = obtainTerms(product1, product2, Prompt, progress_status=progress_status)

        threads = []

        reddit_thread = threading.Thread(target=reddit_scrape, args=(searchTerms, posts, progress_status), daemon=True)
        threads.append(reddit_thread)
        reddit_thread.start()

        if include_hacker_news:
            hn_thread = threading.Thread(target=hacker_news_scrape, args=(searchTerms, posts, progress_status), daemon=True)
            threads.append(hn_thread)
            hn_thread.start()

        for t in threads:
            t.join()

        progress_status["status"] = "Analyzing sentiment..."
        sentiment_message = SentimentAnalysisPrompt(posts,product1,product2)
        analysed_response = sendRequest(sentiment_message)
        print(analysed_response)
        progress_status["status"] = "Generating Article Body"
        articlemessage = ArticlePrompt(analysed_response,product1,product2,article_type,Prompt.extra_txt)
        article = sendRequest(articlemessage)
        progress_status["status"] = "Making a clever title"
        titlemessage = TitlePrompt(article)
        title = sendRequest(titlemessage)
        print(title)
        article_emitter(article,title)
        progress_status["status"] = "Done"

    except Exception as e:
        progress_status["status"] = f"[ERROR] {e}"
        print(f"[ERROR] {e}")
        traceback.print_exception(type(e), e, e.__traceback__)
    finally:
        time.sleep(1)
        stop_event.set()

    