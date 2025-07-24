import os
from dotenv import load_dotenv
from google import genai

current_script_path = os.path.abspath(__file__)
parent_dir = os.path.dirname(current_script_path)
grandparent_dir = os.path.dirname(parent_dir)
load_dotenv(os.path.join(grandparent_dir, '.env'))

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)