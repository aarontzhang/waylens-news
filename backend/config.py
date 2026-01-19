import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DATABASE_URL = "sqlite:///./waylens_news.db"

# News fetching settings
NEWS_LOOKBACK_DAYS = 14  # How far back to look for news
MAX_HEADLINES_PER_COMPANY = 20  # Max headlines to fetch per company

# Claude models
SCORING_MODEL = "claude-3-haiku-20240307"  # Fast/cheap for headline scoring
SUMMARY_MODEL = "claude-opus-4-5-20251101"  # Opus 4.5 for high-quality summaries
