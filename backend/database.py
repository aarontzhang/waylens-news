import sqlite3
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

DATABASE_PATH = "waylens_news.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Initialize database tables."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Companies table with priority fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                search_term TEXT NOT NULL,
                priority_tier INTEGER DEFAULT 4,
                priority_weight INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Articles table with scoring fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                source TEXT,
                published_at TIMESTAMP,
                is_relevant BOOLEAN DEFAULT NULL,
                relevance_reason TEXT,
                summary TEXT,
                significance_score INTEGER DEFAULT 0,
                final_score INTEGER DEFAULT 0,
                news_type TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """)

        # Weekly digests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS digests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT NOT NULL,
                article_ids TEXT NOT NULL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_company
            ON articles (company_id, fetched_at DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_relevant
            ON articles (is_relevant, fetched_at DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_articles_final_score
            ON articles (final_score DESC)
        """)

        # Add new columns to existing tables if they don't exist
        _add_column_if_not_exists(cursor, "companies", "priority_tier", "INTEGER DEFAULT 4")
        _add_column_if_not_exists(cursor, "companies", "priority_weight", "INTEGER DEFAULT 5")
        _add_column_if_not_exists(cursor, "articles", "significance_score", "INTEGER DEFAULT 0")
        _add_column_if_not_exists(cursor, "articles", "final_score", "INTEGER DEFAULT 0")
        _add_column_if_not_exists(cursor, "articles", "news_type", "TEXT")


def _add_column_if_not_exists(cursor, table: str, column: str, definition: str):
    """Safely add a column if it doesn't exist."""
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    except sqlite3.OperationalError:
        pass  # Column already exists


# Company CRUD operations
def get_all_companies():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies ORDER BY priority_tier, category, name")
        return [dict(row) for row in cursor.fetchall()]


def get_company_by_id(company_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_companies_by_category(category: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE category = ? ORDER BY priority_tier, name", (category,))
        return [dict(row) for row in cursor.fetchall()]


def get_companies_by_tier(tier: int):
    """Get all companies in a specific priority tier."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE priority_tier = ? ORDER BY name", (tier,))
        return [dict(row) for row in cursor.fetchall()]


def add_company(name: str, category: str, search_term: Optional[str] = None,
                priority_tier: int = 4, priority_weight: int = 5):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT OR IGNORE INTO companies (name, category, search_term, priority_tier, priority_weight)
               VALUES (?, ?, ?, ?, ?)""",
            (name, category, search_term or name, priority_tier, priority_weight)
        )
        return cursor.lastrowid


def search_companies(query: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM companies WHERE name LIKE ? ORDER BY priority_tier, name",
            (f"%{query}%",)
        )
        return [dict(row) for row in cursor.fetchall()]


# Article CRUD operations
def add_article(company_id: int, title: str, url: str, source: str = None,
                published_at: str = None, significance_score: int = 0,
                final_score: int = 0, news_type: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO articles (company_id, title, url, source, published_at,
                   significance_score, final_score, news_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (company_id, title, url, source, published_at,
                 significance_score, final_score, news_type)
            )
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Article already exists, update scores
            cursor.execute(
                """UPDATE articles SET significance_score = ?, final_score = ?, news_type = ?
                   WHERE url = ?""",
                (significance_score, final_score, news_type, url)
            )
            cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
            row = cursor.fetchone()
            return row["id"] if row else None


def update_article_scores(article_id: int, significance_score: int, final_score: int, news_type: str):
    """Update article scoring fields."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE articles
               SET significance_score = ?, final_score = ?, news_type = ?, processed_at = ?
               WHERE id = ?""",
            (significance_score, final_score, news_type, datetime.now().isoformat(), article_id)
        )


def update_article_relevance(article_id: int, is_relevant: bool, reason: str = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE articles
               SET is_relevant = ?, relevance_reason = ?, processed_at = ?
               WHERE id = ?""",
            (is_relevant, reason, datetime.now().isoformat(), article_id)
        )


def update_article_summary(article_id: int, summary: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE articles SET summary = ? WHERE id = ?",
            (summary, article_id)
        )


def get_articles_for_company(company_id: int, only_relevant: bool = False):
    with get_db() as conn:
        cursor = conn.cursor()
        if only_relevant:
            cursor.execute(
                """SELECT * FROM articles
                   WHERE company_id = ? AND is_relevant = 1
                   ORDER BY final_score DESC, published_at DESC""",
                (company_id,)
            )
        else:
            cursor.execute(
                "SELECT * FROM articles WHERE company_id = ? ORDER BY published_at DESC",
                (company_id,)
            )
        return [dict(row) for row in cursor.fetchall()]


def get_unprocessed_articles(company_id: int = None):
    """Get articles that haven't been triaged yet."""
    with get_db() as conn:
        cursor = conn.cursor()
        if company_id:
            cursor.execute(
                """SELECT * FROM articles
                   WHERE company_id = ? AND is_relevant IS NULL
                   ORDER BY fetched_at DESC""",
                (company_id,)
            )
        else:
            cursor.execute(
                """SELECT * FROM articles
                   WHERE is_relevant IS NULL
                   ORDER BY fetched_at DESC"""
            )
        return [dict(row) for row in cursor.fetchall()]


def get_relevant_articles_without_summary():
    """Get relevant articles that need summarization."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT a.*, c.name as company_name
               FROM articles a
               JOIN companies c ON a.company_id = c.id
               WHERE a.is_relevant = 1 AND a.summary IS NULL
               ORDER BY a.final_score DESC"""
        )
        return [dict(row) for row in cursor.fetchall()]


def get_all_relevant_news(limit: int = 50):
    """Get all relevant news across all companies, ordered by final score."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT a.*, c.name as company_name, c.category as company_category,
                      c.priority_tier, c.priority_weight
               FROM articles a
               JOIN companies c ON a.company_id = c.id
               WHERE a.is_relevant = 1
               ORDER BY a.final_score DESC, a.published_at DESC
               LIMIT ?""",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_top_news(limit: int = 10):
    """Get top N news articles by final score."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT a.*, c.name as company_name, c.category as company_category,
                      c.priority_tier, c.priority_weight
               FROM articles a
               JOIN companies c ON a.company_id = c.id
               WHERE a.significance_score > 0
               ORDER BY a.final_score DESC
               LIMIT ?""",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_recent_articles_for_scoring(days: int = 7):
    """Get recent articles that need scoring."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT a.*, c.name as company_name, c.category as company_category,
                      c.priority_tier, c.priority_weight
               FROM articles a
               JOIN companies c ON a.company_id = c.id
               WHERE a.fetched_at >= datetime('now', ?)
               ORDER BY a.fetched_at DESC""",
            (f"-{days} days",)
        )
        return [dict(row) for row in cursor.fetchall()]


# Digest operations
def save_digest(summary: str, article_ids: list[int]):
    """Save a new digest."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO digests (summary, article_ids) VALUES (?, ?)",
            (summary, ",".join(str(id) for id in article_ids))
        )
        return cursor.lastrowid


def get_latest_digest():
    """Get the most recent digest."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM digests ORDER BY generated_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            digest = dict(row)
            # Parse article_ids back to list
            digest["article_ids"] = [int(id) for id in digest["article_ids"].split(",") if id]
            return digest
        return None


def get_articles_by_ids(article_ids: list[int]):
    """Get articles by their IDs."""
    if not article_ids:
        return []
    with get_db() as conn:
        cursor = conn.cursor()
        placeholders = ",".join("?" * len(article_ids))
        cursor.execute(
            f"""SELECT a.*, c.name as company_name, c.category as company_category
                FROM articles a
                JOIN companies c ON a.company_id = c.id
                WHERE a.id IN ({placeholders})
                ORDER BY a.final_score DESC""",
            article_ids
        )
        return [dict(row) for row in cursor.fetchall()]


def get_categories():
    """Get all unique categories."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM companies ORDER BY category")
        return [row["category"] for row in cursor.fetchall()]


def clear_old_articles(days: int = 30):
    """Remove articles older than specified days."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """DELETE FROM articles
               WHERE fetched_at < datetime('now', ?)""",
            (f"-{days} days",)
        )
        return cursor.rowcount
