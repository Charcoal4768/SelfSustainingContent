import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from . import grandparent_dir, hackerNewsScrape, redditScrape, SearchTermsPrompt

load_dotenv(os.path.join(grandparent_dir, '.env'))

SearchTermsSchema = """
{
  "type": "object",
  "properties": {
    "SearchTerms1": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "SearchTerms2": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "Sebreddit1": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "Subreddit2": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "propertyOrdering": [
    "SearchTerms1",
    "SearchTerms2",
    "Sebreddit1",
    "Subreddit2"
  ],
  "required": [
    "SearchTerms1",
    "SearchTerms2",
    "Sebreddit1",
    "Subreddit2"
  ]
}
"""
TitlesSchema = """
{
  "type": "object",
  "properties": {
    "Title_List": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "Title_List"
  ]
}
"""
SentimentSchema = """
{
  "type": "object",
  "properties": {
    "Product1_brief": {
      "type": "string"
    },
    "Product2_brief": {
      "type": "string"
    },
    "Product1_sentiment_score": {
      "type": "number"
    },
    "Product2_sentiment_score": {
      "type": "number"
    },
    "Product1_rel_comments": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "Product2_rel_comments": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "propertyOrdering": [
    "Product1_brief",
    "Product2_brief",
    "Product1_sentiment_score",
    "Product2_sentiment_score",
    "Product1_rel_comments",
    "Product2_rel_comments"
  ],
  "required": [
    "Product1_brief",
    "Product2_brief",
    "Product1_sentiment_score",
    "Product2_sentiment_score",
    "Product1_rel_comments",
    "Product2_rel_comments"
  ]
}
"""
ArticleSchema = """
"""

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def formatTerms(terms):
    searchTerms1 = terms.get("SearchTerms1", [])
    searchTerms2 = terms.get("SearchTerms2", [])
    subreddit1 = terms.get("Sebreddit1", [])
    subreddit2 = terms.get("Subreddit2", [])

    if not searchTerms1 or not searchTerms2:
        raise ValueError("Search terms cannot be empty")

    if not subreddit1 or not subreddit2:
        raise ValueError("Subreddits cannot be empty")

    subreddit1 = redditScrape.subreddit_validator(subreddit1)
    subreddit2 = redditScrape.subreddit_validator(subreddit2)

    return [searchTerms1, searchTerms2], [subreddit1, subreddit2]

def obtainTerms(product1,product2,Prompt):
    response = client.models.generate_content(
        model=Prompt.model,
        contents=Prompt.message,
        config=types.GenerateContentConfig(
            system_instruction=Prompt.system_prompt,
            response_mime_type="application/json",
            response_schema=json.loads(SearchTermsSchema)
            )
    )
    searchTerms = formatTerms(json.loads(response.text))

    return searchTerms

def startProcess(Prompt):
    posts = []
    product1 = Prompt.product1
    product2 = Prompt.product2
    searchTerms = obtainTerms(product1,product2,Prompt)
    print(f"Search Terms: {searchTerms}")
    links_reddit = redditScrape.search(2, searchTerms[0], searchTerms[1])
    for link in links_reddit:
        post = redditScrape.extract_from_discussion(link)
        posts.append(post)

    test = redditScrape.build_custom_sentiment_output(posts, product1, product2)
    print(test)
    