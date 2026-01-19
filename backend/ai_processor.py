"""
Claude AI processor for news scoring and digest generation.

Pipeline:
1. Pre-filter: Regex patterns exclude stock/marketing noise
2. Score: Claude evaluates significance of each headline
3. Rank: Calculate final_score = significance × company_weight
4. Digest: Generate AI summary of top news
"""

import re
import json
import anthropic
from typing import Optional

from config import ANTHROPIC_API_KEY, SCORING_MODEL, SUMMARY_MODEL

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# Regex patterns to exclude irrelevant articles BEFORE Claude processing
EXCLUSION_PATTERNS = [
    # Stock/Market movement
    r"stock\s+(hits|falls|rises|drops|jumps|climbs|sinks|soars|plunges)",
    r"shares\s+(up|down|fall|rise|jump|drop|surge|tumble)",
    r"52-week\s+(high|low)",
    r"price\s+target",
    r"market\s+cap",
    r"trading\s+at\s+\$",
    r"moving\s+average",
    r"analyst\s+(upgrades?|downgrades?|rating)",
    r"earnings\s+(beat|miss|report)",
    r"\$[A-Z]{1,5}\s+stock",  # Ticker symbols
    r"NYSE|NASDAQ|S&P\s*500",
    r"buy\s+rating|sell\s+rating|hold\s+rating",
    r"valuation|overvalued|undervalued",
    # Investment/Portfolio
    r"hedge\s+fund",
    r"institutional\s+(buying|selling|investor)",
    r"portfolio\s+(adds?|sells?|holds?)",
    r"shares\s+(purchased|sold)\s+by",
    # Marketing/Events
    r"sponsors?\s+(event|tournament|game|team)",
    r"community\s+event",
    r"awards?\s+(ceremony|gala|dinner)",
    r"play\s+days?",
]


def pre_filter_headline(title: str) -> tuple[bool, Optional[str]]:
    """
    Check if headline should be excluded based on regex patterns.
    Returns (should_exclude, reason).
    """
    title_lower = title.lower()
    for pattern in EXCLUSION_PATTERNS:
        if re.search(pattern, title_lower, re.IGNORECASE):
            return True, f"Matched exclusion pattern: {pattern[:30]}"
    return False, None


def score_headlines_batch(articles: list[dict], batch_size: int = 50) -> list[dict]:
    """
    Score a batch of headlines using Claude, processing in smaller batches.

    Args:
        articles: List of dicts with 'title', 'company_name', 'priority_weight'
        batch_size: Number of articles to process per API call

    Returns:
        List with added 'significance_score', 'news_type', 'relevance_reason'
    """
    if not articles:
        return []

    if not client:
        # No API key - mark all as low relevance
        for a in articles:
            a['significance_score'] = 0
            a['news_type'] = 'UNSCORED'
            a['relevance_reason'] = 'API key not configured'
        return articles

    # Pre-filter with regex
    filtered_articles = []
    for article in articles:
        should_exclude, reason = pre_filter_headline(article.get('title', ''))
        if should_exclude:
            article['significance_score'] = 0
            article['news_type'] = 'EXCLUDED'
            article['relevance_reason'] = reason
            article['is_relevant'] = False
        else:
            filtered_articles.append(article)

    if not filtered_articles:
        return articles

    # Process in batches to avoid large JSON responses
    for batch_start in range(0, len(filtered_articles), batch_size):
        batch = filtered_articles[batch_start:batch_start + batch_size]
        _score_batch(batch)

    return articles


def _score_batch(filtered_articles: list[dict]) -> None:
    """Score a single batch of articles with Claude."""
    # Build prompt for Claude
    articles_text = "\n".join([
        f"{i+1}. [{a.get('company_name', 'Unknown')}] {a.get('title', '')}"
        for i, a in enumerate(filtered_articles)
    ])

    prompt = f"""You are a business intelligence analyst for Waylens, a fleet safety camera company.
Score each headline's significance for sales intelligence.

SCORING SCALE (be strict - most news is NOT significant):
- 100: Acquisition or Merger (company being bought/buying another)
- 95: IPO or Major Funding (Series B+, $50M+ raises)
- 90: New Product Launch (dashcams, telematics, AI safety features)
- 85: Major Partnership (OEM deals, large carrier partnerships)
- 75: Leadership Change (CEO, CTO, VP Safety/Risk/Fleet)
- 70: Major Contract Win ($1M+, 500+ vehicles)
- 65: Regulatory/Compliance news (FMCSA, DOT requirements)
- 60: Market Expansion (new regions, verticals)
- 50: Technology Update (AI features, platform improvements)
- 30: General Business (routine announcements)
- 0: IRRELEVANT (stock price, marketing, unrelated mentions)

COMPETITORS TO WATCH: Samsara, Motive, Lytx, Netradyne, Geotab

HEADLINES:
{articles_text}

Return ONLY a JSON array (no markdown):
[
  {{"index": 1, "score": 90, "type": "NEW_PRODUCT", "reason": "Competitor launches AI dashcam"}},
  {{"index": 2, "score": 0, "type": "EXCLUDED", "reason": "Stock price movement"}}
]

Be AGGRESSIVE in filtering. Score 0 for anything not clearly business-significant."""

    try:
        response = client.messages.create(
            model=SCORING_MODEL,  # Use fast Haiku for scoring
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text.strip()

        # Clean up response (remove markdown if present)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        # Fix common JSON issues from LLM responses
        response_text = response_text.strip()
        # Remove trailing commas before ] or }
        response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)
        # Ensure it starts with [ and ends with ]
        if not response_text.startswith('['):
            start = response_text.find('[')
            if start != -1:
                response_text = response_text[start:]
        if not response_text.endswith(']'):
            end = response_text.rfind(']')
            if end != -1:
                response_text = response_text[:end+1]

        results = json.loads(response_text)
        results_map = {r['index']: r for r in results}

        for i, article in enumerate(filtered_articles):
            result = results_map.get(i + 1, {})
            article['significance_score'] = result.get('score', 0)
            article['news_type'] = result.get('type', 'UNKNOWN')
            article['relevance_reason'] = result.get('reason', '')
            article['is_relevant'] = article['significance_score'] > 0

    except Exception as e:
        print(f"Error scoring headlines: {e}")
        # Log the problematic response for debugging
        if 'response_text' in dir():
            print(f"Response text (first 500 chars): {response_text[:500] if response_text else 'None'}")
        for article in filtered_articles:
            article['significance_score'] = 0
            article['news_type'] = 'ERROR'
            article['relevance_reason'] = str(e)[:100]


def calculate_final_scores(articles: list[dict]) -> list[dict]:
    """
    Calculate final_score prioritizing news significance over company importance.

    Formula: (significance_score * 2) + (priority_weight * 0.5)

    This ensures important news (acquisitions, product launches) from smaller
    companies ranks higher than routine news from major competitors.

    Examples:
    - Acquisition (100) at Tier 4 company (weight 5): (100*2) + (5*0.5) = 202.5
    - Routine news (30) at Tier 1 company (weight 100): (30*2) + (100*0.5) = 110
    """
    for article in articles:
        significance = article.get('significance_score', 0)
        weight = article.get('priority_weight', 5)
        article['final_score'] = (significance * 2) + (weight * 0.5)
    return articles


def generate_digest(top_articles: list[dict]) -> str:
    """
    Generate an AI summary digest of the top news.

    Args:
        top_articles: List of top-scored articles with company info

    Returns:
        2-3 paragraph summary for the sales team
    """
    if not top_articles:
        return "No significant news this week."

    if not client:
        return "Digest unavailable - API key not configured."

    # Build context for Claude
    news_items = "\n".join([
        f"- [{a.get('company_name')}] {a.get('title')} (Type: {a.get('news_type')}, Score: {a.get('final_score')})"
        for a in top_articles
    ])

    prompt = f"""You are a business intelligence analyst writing a weekly digest for the Waylens sales team.

Waylens makes cameras and software for fleet vehicles to improve safety. Key competitors: Samsara, Motive, Lytx, Netradyne.

Write a concise 2-3 paragraph summary of this week's most significant news. Structure:
1. Competitor activity (product launches, partnerships, major wins)
2. Prospect/customer developments relevant to fleet safety
3. Actionable sales insights

Guidelines:
- Be direct and professional
- Use **bold** for company names and key terms
- No emojis or casual language
- Focus on business implications

THIS WEEK'S TOP NEWS:
{news_items}

Write the digest now (paragraphs only, no headers or bullet points):"""

    try:
        response = client.messages.create(
            model=SUMMARY_MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    except Exception as e:
        print(f"Error generating digest: {e}")
        return f"Error generating digest: {str(e)[:100]}"


async def process_and_score_articles(articles: list[dict], companies_map: dict) -> list[dict]:
    """
    Full pipeline: enrich articles with company info, score, calculate final scores.

    Args:
        articles: Raw articles from news fetcher
        companies_map: Dict mapping company_id to company info

    Returns:
        Scored and ranked articles
    """
    # Enrich with company info
    for article in articles:
        company = companies_map.get(article.get('company_id'), {})
        article['company_name'] = company.get('name', 'Unknown')
        article['priority_weight'] = company.get('priority_weight', 5)
        article['priority_tier'] = company.get('priority_tier', 4)

    # Score with Claude
    scored = score_headlines_batch(articles)

    # Calculate final scores
    ranked = calculate_final_scores(scored)

    return ranked


def get_top_articles(articles: list[dict], limit: int = 10) -> list[dict]:
    """
    Get top N articles by final score, ensuring company diversity.
    """
    # Sort by final score
    sorted_articles = sorted(
        [a for a in articles if a.get('final_score', 0) > 0],
        key=lambda x: x.get('final_score', 0),
        reverse=True
    )

    # Select top articles with diversity (max 2 per company)
    selected = []
    company_counts = {}

    for article in sorted_articles:
        if len(selected) >= limit:
            break

        company_name = article.get('company_name', 'Unknown')
        if company_counts.get(company_name, 0) < 2:
            selected.append(article)
            company_counts[company_name] = company_counts.get(company_name, 0) + 1

    return selected


# Keep old functions for backward compatibility
def triage_headlines(company_name: str, headlines: list[dict]) -> list[dict]:
    """Legacy function - redirects to new scoring system."""
    for h in headlines:
        h['company_name'] = company_name
        h['priority_weight'] = 50  # Default weight
    return score_headlines_batch(headlines)


def summarize_article(company_name: str, title: str, content: str) -> Optional[str]:
    """Generate a summary for a single article."""
    if not content or not client:
        return None

    prompt = f"""Summarize this article about "{company_name}" for the WayLens sales team.
Focus on key facts and sales implications. Be concise (2-3 sentences).

Title: {title}
Content: {content[:3000]}"""

    try:
        response = client.messages.create(
            model=SUMMARY_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Error summarizing: {e}")
        return None


async def process_company_news(company_id: int, company_name: str, articles: list[dict]) -> dict:
    """Process news for a single company - scores headlines."""
    from database import add_article, update_article_scores

    stats = {'triaged': 0, 'relevant': 0, 'summarized': 0}

    if not articles:
        return stats

    # Add company info for scoring
    for article in articles:
        article['company_name'] = company_name
        article['company_id'] = company_id
        article['priority_weight'] = 50  # Will be updated from DB in full pipeline

    # Score headlines
    scored = score_headlines_batch(articles)
    scored = calculate_final_scores(scored)
    stats['triaged'] = len(scored)

    # Save to database
    for article in scored:
        article_id = add_article(
            company_id=company_id,
            title=article.get('title', ''),
            url=article.get('url', ''),
            source=article.get('source'),
            published_at=article.get('published_at'),
            significance_score=article.get('significance_score', 0),
            final_score=article.get('final_score', 0),
            news_type=article.get('news_type')
        )

        if article_id and article.get('significance_score', 0) > 0:
            stats['relevant'] += 1

    return stats
