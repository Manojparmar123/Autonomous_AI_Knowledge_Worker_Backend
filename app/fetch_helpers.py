import os
import logging
import requests
from fastapi import HTTPException

from .utils.vector_db import upsert_embeddings
from .utils.fallback_llm import get_embedding_with_fallback

logger = logging.getLogger(__name__)

# -------------------- NewsAPI Helper -------------------- #
def fetch_news_helper(topic: str = "AI", limit: int = 5, do_embed: bool = True):
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    if not NEWS_API_KEY:
        raise HTTPException(status_code=500, detail="NEWS_API_KEY not set")

    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=publishedAt&pageSize={limit}&apiKey={NEWS_API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning(f"⚠️ NewsAPI request failed: {e}")
        return []

    if data.get("status") != "ok":
        logger.warning(f"⚠️ NewsAPI error: {data}")
        return []

    articles = []
    for i, art in enumerate(data.get("articles", [])[:limit]):
        title = art.get("title", "")
        desc = art.get("description", "")
        text = f"{title} {desc}".strip()
        if not text:
            continue

        emb = get_embedding_with_fallback(text) if do_embed else None
        articles.append({
            "doc_id": f"news_{i}",
            "chunk_id": f"chunk_{i}",
            "text": text,
            "source": art.get("url", "unknown"),
            "embedding": emb
        })

    if articles and do_embed:
        upsert_embeddings(articles, provider="newsapi")

    return articles


# -------------------- Alpha Vantage Stock Helper -------------------- #
def fetch_stock_helper(symbol: str = "AAPL", limit: int = 5, do_embed: bool = True):
    ALPHA_KEY = os.getenv("ALPHA_KEY")
    if not ALPHA_KEY:
        raise HTTPException(status_code=500, detail="ALPHA_KEY not set")

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning(f"⚠️ AlphaVantage request failed: {e}")
        return []

    if "Error Message" in data or "Note" in data:
        logger.warning(f"⚠️ AlphaVantage error: {data}")
        return []

    daily = data.get("Time Series (Daily)", {})
    articles = []
    for i, (date, metrics) in enumerate(list(daily.items())[:limit]):
        text = f"{symbol} on {date}: Open {metrics['1. open']}, Close {metrics['4. close']}, Volume {metrics['5. volume']}"
        emb = get_embedding_with_fallback(text) if do_embed else None
        articles.append({
            "doc_id": f"{symbol}_{date}",
            "chunk_id": f"chunk_{i}",
            "text": text,
            "source": "Alpha Vantage",
            "embedding": emb
        })

    if articles and do_embed:
        upsert_embeddings(articles, provider="alphavantage")

    return articles


# -------------------- Google Search Helper -------------------- #
def search_web_helper(query: str, limit: int = 5, do_embed: bool = True):
    GOOGLE_KEY = os.getenv("GOOGLE_KEY")
    CX_ID = os.getenv("CX_ID")
    if not GOOGLE_KEY or not CX_ID:
        raise HTTPException(status_code=500, detail="GOOGLE_KEY or CX_ID not set")

    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_KEY}&cx={CX_ID}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning(f"⚠️ Google search request failed: {e}")
        return []

    if "error" in data:
        logger.warning(f"⚠️ Google API error: {data}")
        return []

    items = data.get("items", [])
    results = []
    for i, item in enumerate(items[:limit]):
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        text = f"{title} {snippet}".strip()
        if not text:
            continue

        emb = get_embedding_with_fallback(text) if do_embed else None
        results.append({
            "doc_id": f"google_{i}",
            "chunk_id": f"chunk_{i}",
            "text": text,
            "source": item.get("link", "unknown"),
            "embedding": emb
        })

    if results and do_embed:
        upsert_embeddings(results, provider="google")

    return results
