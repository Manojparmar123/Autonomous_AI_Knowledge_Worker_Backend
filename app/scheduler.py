# apps/backend/app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from sqlmodel import Session
from .db import engine
from .models import Report
from .fetch_helpers import (
    fetch_news_helper,
    fetch_stock_helper,
    search_web_helper
)
from .utils.fallback_llm import generate_response_with_fallback

# --- Logging setup --- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Scheduler instance --- #
scheduler = BackgroundScheduler()

# --- Helper: Save report into DB --- #
def save_report(kind: str, content: str):
    """Save summarized report into DB"""
    with Session(engine) as session:
        report = Report(kind=kind, content=content)
        session.add(report)
        session.commit()
        logger.info(f"✅ Saved {kind} report at {report.created_at}")

# --- Job functions --- #
def scheduled_news_summary():
    run_job("news", lambda: fetch_news_helper("technology"), limit=5, prompt="Summarize today's news: ")

def scheduled_stock_check():
    run_job("stock", lambda: fetch_stock_helper("AAPL"), limit=3, prompt="Summarize stock performance: ")

def scheduled_google_trends():
    run_job("search", lambda: search_web_helper("AI trends 2025"), limit=5, prompt="Summarize web search results: ")

# --- Generic Job Runner --- #
def run_job(kind: str, fetch_fn, limit: int, prompt: str):
    try:
        data = fetch_fn()
        if not data:
            logger.warning(f"⚠️ No {kind} data fetched.")
            return

        text = " ".join([item["text"] for item in data[:limit]])
        summary = generate_response_with_fallback(f"{prompt}{text}")
        save_report(kind, summary)
        logger.info(f"✅ {kind} job completed.")
    except Exception as e:
        logger.error(f"❌ Error in {kind} job: {e}")

# --- Job registry for manual trigger --- #
JOB_REGISTRY = {
    "news": scheduled_news_summary,
    "stock": scheduled_stock_check,
    "search": scheduled_google_trends,
}

def run_manual_job(job_name: str):
    """Manually run a job by name"""
    job = JOB_REGISTRY.get(job_name)
    if not job:
        raise ValueError(f"Unknown job: {job_name}")
    job()

# --- Start Scheduler --- #
def start_scheduler():
    # Run at fixed times (cron style)
    scheduler.add_job(scheduled_news_summary, "cron", hour=9, minute=0)    # daily 9:00 AM
    scheduler.add_job(scheduled_stock_check, "interval", hours=6)          # every 6 hours
    scheduler.add_job(scheduled_google_trends, "cron", hour=10, minute=0)  # daily 10:00 AM

    scheduler.start()
    logger.info("🚀 Scheduler started (news 9 AM, stock 6h, trends 10 AM)")


