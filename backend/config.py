import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.7
GROQ_MAX_TOKENS = 1024

SCRAPER_TIMEOUT = 15
SCRAPER_STRIP_TAGS = ["script", "style"]
SCRAPER_USER_AGENT = "RohithAIChatbot/1.0"
SCRAPER_MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5 MB

CONTENT_PREVIEW_LENGTH = 1000

ENV = os.getenv("ENV", "production")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
TRAIN_API_KEY = os.getenv("TRAIN_API_KEY")
