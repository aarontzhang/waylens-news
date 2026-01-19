"""
FastAPI backend for WayLens News Aggregator.
Provides endpoints for companies, news, and refresh operations.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from database import (
    init_db,
    get_all_companies,
    get_company_by_id,
    get_companies_by_category,
    search_companies,
    get_articles_for_company,
    get_all_relevant_news,
    get_categories,
    get_unprocessed_articles,
    clear_old_articles,
    get_top_news,
    save_digest,
    get_latest_digest,
    get_articles_by_ids,
)
from companies import seed_companies
import database as db_module
from news_fetcher import fetch_news_for_company
from ai_processor import (
    process_company_news,
    score_headlines_batch,
    calculate_final_scores,
    generate_digest,
    get_top_articles,
)

# Initialize FastAPI app
app = FastAPI(
    title="WayLens News Aggregator",
    description="AI-powered news aggregation for WayLens prospect companies",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup():
    """Initialize database and seed companies on startup."""
    init_db()
    seed_companies(db_module)


# Response models
class CompanyResponse(BaseModel):
    id: int
    name: str
    category: str
    search_term: str


class ArticleResponse(BaseModel):
    id: int
    company_id: int
    title: str
    url: str
    source: Optional[str]
    published_at: Optional[str]
    is_relevant: Optional[bool]
    relevance_reason: Optional[str]
    summary: Optional[str]
    fetched_at: str


class RefreshStats(BaseModel):
    company_id: int
    company_name: str
    triaged: int
    relevant: int
    summarized: int


# ============== Company Endpoints ==============

@app.get("/api/companies")
async def list_companies(category: Optional[str] = None):
    """Get all companies, optionally filtered by category."""
    if category:
        companies = get_companies_by_category(category)
    else:
        companies = get_all_companies()
    return {"companies": companies}


@app.get("/api/companies/search")
async def search_companies_endpoint(q: str):
    """Search companies by name."""
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    companies = search_companies(q)
    return {"companies": companies}


@app.get("/api/companies/{company_id}")
async def get_company(company_id: int):
    """Get a specific company by ID."""
    company = get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@app.get("/api/companies/{company_id}/news")
async def get_company_news(company_id: int, only_relevant: bool = False):
    """Get news articles for a specific company."""
    company = get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    articles = get_articles_for_company(company_id, only_relevant=only_relevant)
    return {
        "company": company,
        "articles": articles
    }


# ============== News Feed Endpoints ==============

@app.get("/api/news")
async def get_news_feed(limit: int = 50, category: Optional[str] = None):
    """Get the main news feed with all relevant articles."""
    articles = get_all_relevant_news(limit=limit)

    # Filter by category if specified
    if category:
        articles = [a for a in articles if a.get('company_category') == category]

    return {"articles": articles}


@app.get("/api/categories")
async def list_categories():
    """Get all company categories."""
    categories = get_categories()
    return {"categories": categories}


# ============== Digest Endpoints ==============

@app.get("/api/digest")
async def get_digest():
    """
    Get the latest AI digest with summary and sources.
    Returns the most recent generated digest.
    """
    digest = get_latest_digest()

    if not digest:
        return {
            "summary": "No digest available yet. Click 'Generate Digest' to create one.",
            "generated_at": None,
            "sources": []
        }

    # Get the source articles
    sources = get_articles_by_ids(digest.get("article_ids", []))

    return {
        "summary": digest.get("summary", ""),
        "generated_at": digest.get("generated_at"),
        "sources": sources
    }


@app.post("/api/digest/refresh")
async def refresh_digest(background_tasks: BackgroundTasks):
    """
    Generate a new digest:
    1. Fetch news for high-priority companies (Tier 1 & 2)
    2. Score and rank all articles
    3. Select top 10 most important
    4. Generate AI summary
    """
    global refresh_status

    if refresh_status.get("running"):
        raise HTTPException(status_code=409, detail="A refresh is already in progress")

    background_tasks.add_task(generate_digest_task)

    return {
        "message": "Digest generation started",
        "status_endpoint": "/api/refresh-status"
    }


async def generate_digest_task():
    """Background task to generate a new digest."""
    global refresh_status

    refresh_status["running"] = True
    refresh_status["progress"] = 0
    refresh_status["current"] = "Starting digest generation..."

    try:
        # Get high-priority companies (Tier 1 & 2) - ~33 companies
        all_companies = get_all_companies()
        companies = [c for c in all_companies if c.get("priority_tier", 4) <= 2]

        refresh_status["total"] = len(companies)

        all_articles = []
        loop = asyncio.get_event_loop()

        # Helper function to fetch news for a single company
        def fetch_single_company(company):
            try:
                search_term = company.get("search_term") or company["name"]
                articles = fetch_news_for_company(search_term)
                if articles:
                    for article in articles:
                        article["company_id"] = company["id"]
                        article["company_name"] = company["name"]
                        article["priority_weight"] = company.get("priority_weight", 5)
                        article["priority_tier"] = company.get("priority_tier", 4)
                    return articles
                return []
            except Exception as e:
                print(f"Error fetching {company['name']}: {e}")
                return []

        # Fetch news in parallel batches for speed
        batch_size = 10
        with ThreadPoolExecutor(max_workers=10) as executor:
            for batch_start in range(0, len(companies), batch_size):
                batch = companies[batch_start:batch_start + batch_size]
                batch_end = min(batch_start + batch_size, len(companies))

                refresh_status["progress"] = batch_start
                refresh_status["current"] = f"Fetching: batch {batch_start//batch_size + 1} ({batch_start+1}-{batch_end})"

                # Run batch in parallel
                futures = [loop.run_in_executor(executor, fetch_single_company, c) for c in batch]
                results = await asyncio.gather(*futures)

                for articles in results:
                    all_articles.extend(articles)

                await asyncio.sleep(0.1)  # Small delay between batches

        refresh_status["current"] = "Scoring articles with AI..."
        refresh_status["progress"] = 0
        refresh_status["total"] = 0
        await asyncio.sleep(0.1)  # Yield to allow status poll

        # Score all articles in batch (run in thread pool to not block event loop)
        if all_articles:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                scored_articles = await loop.run_in_executor(
                    executor, score_headlines_batch, all_articles
                )
            scored_articles = calculate_final_scores(scored_articles)

            # Save articles to database
            for article in scored_articles:
                db_module.add_article(
                    company_id=article.get("company_id"),
                    title=article.get("title", ""),
                    url=article.get("url", ""),
                    source=article.get("source"),
                    published_at=article.get("published_at"),
                    significance_score=article.get("significance_score", 0),
                    final_score=article.get("final_score", 0),
                    news_type=article.get("news_type")
                )

            # Get top articles
            top_articles = get_top_articles(scored_articles, limit=10)

            refresh_status["current"] = "Generating AI summary..."
            await asyncio.sleep(0.1)  # Yield to allow status poll

            # Generate digest summary (run in thread pool to not block event loop)
            if top_articles:
                with ThreadPoolExecutor() as executor:
                    summary = await loop.run_in_executor(
                        executor, generate_digest, top_articles
                    )
                article_ids = [a.get("id") for a in get_top_news(10) if a.get("id")]

                # Save digest
                save_digest(summary, article_ids)

        refresh_status["current"] = "Complete!"

    except Exception as e:
        print(f"Error generating digest: {e}")
        refresh_status["current"] = f"Error: {str(e)[:50]}"

    finally:
        refresh_status["running"] = False


# ============== Refresh Endpoints ==============

@app.post("/api/refresh/{company_id}")
async def refresh_company(company_id: int):
    """
    Fetch fresh news for a company and process with AI.
    This is synchronous and may take 10-30 seconds.
    """
    company = get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Fetch news from Google News RSS
    search_term = company.get("search_term") or company["name"]
    articles = fetch_news_for_company(search_term)

    if not articles:
        return {
            "company_id": company_id,
            "company_name": company["name"],
            "triaged": 0,
            "relevant": 0,
            "summarized": 0,
            "message": "No news found"
        }

    # Process with AI (triage + summarize)
    stats = await process_company_news(company_id, company["name"], articles)

    return {
        "company_id": company_id,
        "company_name": company["name"],
        **stats,
        "message": f"Processed {stats['triaged']} articles, {stats['relevant']} relevant, {stats['summarized']} summarized"
    }


# Background task for bulk refresh
refresh_status = {"running": False, "progress": 0, "total": 0, "current": None}


async def refresh_all_companies_task():
    """Background task to refresh all companies."""
    global refresh_status

    companies = get_all_companies()
    refresh_status["total"] = len(companies)
    refresh_status["running"] = True

    for i, company in enumerate(companies):
        refresh_status["progress"] = i
        refresh_status["current"] = company["name"]

        try:
            search_term = company.get("search_term") or company["name"]
            articles = fetch_news_for_company(search_term)

            if articles:
                await process_company_news(company["id"], company["name"], articles)

            # Small delay to avoid rate limiting
            await asyncio.sleep(1)

        except Exception as e:
            print(f"Error refreshing {company['name']}: {e}")
            continue

    refresh_status["running"] = False
    refresh_status["current"] = None


@app.post("/api/refresh-all")
async def refresh_all(background_tasks: BackgroundTasks):
    """
    Trigger a refresh of all companies in the background.
    Returns immediately, check /api/refresh-status for progress.
    """
    global refresh_status

    if refresh_status["running"]:
        raise HTTPException(status_code=409, detail="Refresh already in progress")

    background_tasks.add_task(refresh_all_companies_task)

    return {
        "message": "Bulk refresh started",
        "status_endpoint": "/api/refresh-status"
    }


@app.get("/api/refresh-status")
async def get_refresh_status():
    """Get the status of a bulk refresh operation."""
    return refresh_status


# ============== Maintenance Endpoints ==============

@app.delete("/api/articles/old")
async def cleanup_old_articles(days: int = 30):
    """Remove articles older than specified days."""
    deleted = clear_old_articles(days)
    return {"deleted": deleted, "message": f"Removed {deleted} articles older than {days} days"}


@app.get("/api/stats")
async def get_stats():
    """Get overall statistics."""
    companies = get_all_companies()
    articles = get_all_relevant_news(limit=1000)
    unprocessed = get_unprocessed_articles()

    categories = {}
    for company in companies:
        cat = company["category"]
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_companies": len(companies),
        "total_relevant_articles": len(articles),
        "unprocessed_articles": len(unprocessed),
        "companies_by_category": categories
    }


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
