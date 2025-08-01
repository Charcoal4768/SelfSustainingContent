import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel

current_script_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(current_script_path)
grandparent_dir = os.path.dirname(parent_dir)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

class Prompt:
    def __init__(self, template_filename=None, default_filename=None, default_schema_name=None, model="gemini-2.5-pro"):
        if default_filename is None:
            raise ValueError("You must specify a default filename for the prompt template.")
        if default_schema_name is None:
            raise ValueError("You must specify an output Schema")
        
        system_prompt_path = template_filename or os.path.join(parent_dir, "prompts", default_filename)
        schema_path = os.path.join(parent_dir,"schemas",default_schema_name)
        if not os.path.exists(system_prompt_path):
            raise FileNotFoundError(f"Prompt template not found at {system_prompt_path}")
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Prompt template not found at {schema_path}")

        with open(system_prompt_path, "r") as f:
            self.system_prompt = f.read()
        
        with open(schema_path,"r") as f:
            self.schema = json.load(f)

        self.model = model
        self.message = self.build_message()

    def build_message(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.message}"


class SearchTermsPrompt(Prompt):
    def __init__(self, product1, product2, extra_txt="", template_path=None):
        if product1 is None or product2 is None:
            raise ValueError("Product terms cannot be None")

        self.product1 = product1
        self.product2 = product2
        self.extra_txt = extra_txt

        super().__init__(
            template_filename=template_path,
            default_filename="search_terms.txt",
            default_schema_name="search_terms.json",
            model="gemini-2.5-flash"
        )

        self.message = (
            f"| Content: Product_1 -> {product1}, "
            f"Product_2 -> {product2} | Extra Information: {extra_txt} |"
        )

class SentimentAnalysisPrompt(Prompt):
    def __init__(self, posts, product1="Product A", product2="Product B", template_path=None):
        if not posts:
            raise ValueError("Posts cannot be empty")

        self.posts = posts
        self.product1 = product1
        self.product2 = product2

        super().__init__(
            template_filename=template_path,
            default_filename="sentiment_analysis.txt",
            default_schema_name="sentiment_analysis.json",
            model="gemini-2.5-pro"
        )

        self.message = format_sentiment_input(posts, product1, product2)

class ArticlePrompt(Prompt):
    def __init__(self, sentiments, product1="Product A", product2="Product B", article_type="listicle", template_path=None, model="gemini-2.5-pro"):
        if not sentiments:
            raise ValueError("A sentiment analysis is required to generate the article.")

        super().__init__(
            template_filename=template_path,
            default_filename="articles.txt",
            default_schema_name="articles.json",
            model=model
        )

        self.message = (f"A sentiment analysis has been conducted on product 1: {product1} and product 2: {product2}. Generate a user article of type {article_type} based on the community's sentiments:\n {sentiments}")

class TitlePrompt(Prompt):
    def __init__(self, article_body, template_path=None, model="gemini-2.5-pro"):
        if not article_body:
            raise ValueError("Article Body cannot be empty")

        super().__init__(
            template_filename=template_path,
            default_filename="title.txt",
            default_schema_name="title.json",
            model=model
        )

        self.message = (
            f"Generate a title utilizing clever psychological hooks and strong emotions to get the reader's attention and rank high in google searches.\n"
            f"Article Body: {article_body}"
        )

def format_sentiment_input(posts, product1="Product A", product2="Product B"):
    lines = [f"[[SENTIMENT]] | Product_1: {product1} | Product_2: {product2} |"]

    for post in posts:
        title = post.get("title", "Untitled").strip()
        comments = post.get("comments", [])[:5]

        lines.append(f"{title}:")
        lines.append("---")
        for comment in comments:
            lines.append(f"COMMENT: {comment.strip()}")
        lines.append("---")

    lines.append("|")
    return "\n".join(lines)

def sendRequest(prompt: Prompt):
    response = client.models.generate_content(
        model=prompt.model,
        contents=prompt.message,
        config=types.GenerateContentConfig(
            system_instruction=prompt.system_prompt,
            response_mime_type="application/json",
            response_schema=prompt.schema
        )
    )
    return json.loads(response.text)

#TODO: title promt, article prompt, etc, etc, schema not ready yet