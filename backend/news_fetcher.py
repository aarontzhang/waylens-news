"""
Google News RSS fetcher for company news.
Uses the free Google News RSS feed to get recent headlines.
"""

import feedparser
from datetime import datetime
from urllib.parse import quote_plus
from typing import Optional
import httpx
from bs4 import BeautifulSoup

from config import NEWS_LOOKBACK_DAYS, MAX_HEADLINES_PER_COMPANY


def build_google_news_url(search_term: str, days: int = NEWS_LOOKBACK_DAYS) -> str:
    """
    Build a Google News RSS URL for the given search term.

    Args:
        search_term: The company name or search query
        days: How many days back to search (default 14)

    Returns:
        Google News RSS URL
    """
    encoded_query = quote_plus(f"{search_term} when:{days}d")
    return f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"


def parse_published_date(date_str: str) -> Optional[str]:
    """Parse RSS date string to ISO format."""
    try:
        # Google News uses RFC 2822 format
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except Exception:
        return None


def fetch_news_for_company(search_term: str, max_results: int = MAX_HEADLINES_PER_COMPANY) -> list[dict]:
    """
    Fetch news headlines for a company from Google News RSS.

    Args:
        search_term: The search query (usually company name)
        max_results: Maximum number of headlines to return

    Returns:
        List of article dicts with title, url, source, published_at
    """
    url = build_google_news_url(search_term)

    try:
        feed = feedparser.parse(url)

        articles = []
        for entry in feed.entries[:max_results]:
            # Extract source from title (Google News format: "Title - Source")
            title = entry.get("title", "")
            source = None
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                if len(parts) == 2:
                    title = parts[0]
                    source = parts[1]

            article = {
                "title": title,
                "url": entry.get("link", ""),
                "source": source,
                "published_at": parse_published_date(entry.get("published", ""))
            }
            articles.append(article)

        return articles

    except Exception as e:
        print(f"Error fetching news for '{search_term}': {e}")
        return []


async def fetch_article_content(url: str, timeout: float = 10.0) -> Optional[str]:
    """
    Fetch the full content of an article from its URL.

    Args:
        url: The article URL
        timeout: Request timeout in seconds

    Returns:
        Extracted article text or None if failed
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                url,
                timeout=timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                }
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
                element.decompose()

            # Try to find the main article content
            article_content = None

            # Look for common article containers
            selectors = [
                "article",
                "[role='main']",
                ".article-content",
                ".article-body",
                ".post-content",
                ".entry-content",
                ".story-body",
                "main",
            ]

            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    article_content = element
                    break

            if article_content is None:
                article_content = soup.body

            if article_content:
                # Get text and clean it up
                text = article_content.get_text(separator="\n", strip=True)
                # Limit to first ~5000 chars to avoid huge content
                return text[:5000] if len(text) > 5000 else text

            return None

    except Exception as e:
        print(f"Error fetching article content from {url}: {e}")
        return None


def fetch_news_batch(companies: list[dict]) -> dict:
    """
    Fetch news for multiple companies.

    Args:
        companies: List of company dicts with 'id', 'name', 'search_term'

    Returns:
        Dict mapping company_id to list of articles
    """
    results = {}

    for company in companies:
        company_id = company["id"]
        search_term = company.get("search_term") or company["name"]

        articles = fetch_news_for_company(search_term)
        results[company_id] = articles

    return results
