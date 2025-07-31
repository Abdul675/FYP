from langchain_openai import ChatOpenAI
import os 
from dotenv import load_dotenv
load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_openai_model():
    return "gpt-4o"  # or "gpt-4", "gpt-3.5-turbo", etc.
