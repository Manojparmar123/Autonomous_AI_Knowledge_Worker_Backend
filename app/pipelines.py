# import logging
# import asyncio
# from sqlmodel import Session
# from apscheduler.schedulers.background import BackgroundScheduler
# from langchain.prompts import PromptTemplate
# from langchain.schema.runnable import RunnableLambda, RunnableSequence

# from .db import engine
# from .models import Report
# from .fetch_helpers import fetch_news_helper, fetch_stock_helper, search_web_helper
# from .utils.fallback_llm import generate_response_with_fallback

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # ---------------------------
# # Helper: Save report into DB
# # ---------------------------
# def save_report(kind: str, content: str):
#     with Session(engine) as session:
#         report = Report(kind=kind, content=content)
#         session.add(report)
#         session.commit()
#         logger.info(f"✅ Saved {kind} report at {report.created_at}")

# # ---------------------------
# # Prompt Templates
# # ---------------------------
# news_prompt = PromptTemplate.from_template(
#     "Summarize the following news article:\n\n{text}"
# )

# stock_prompt = PromptTemplate.from_template(
#     "Analyze the stock performance for {symbol} given this data:\n\n{text}"
# )

# trends_prompt = PromptTemplate.from_template(
#     "Identify the main trends from the following search results:\n\n{text}"
# )

# # ---------------------------
# # Runnable Wrappers
# # ---------------------------
# news_llm = RunnableLambda(lambda x: generate_response_with_fallback(x))
# stock_llm = RunnableLambda(lambda x: generate_response_with_fallback(x))
# trends_llm = RunnableLambda(lambda x: generate_response_with_fallback(x))

# # ---------------------------
# # Pipelines
# # ---------------------------
# news_pipeline: RunnableSequence = news_prompt | news_llm
# stock_pipeline: RunnableSequence = stock_prompt | stock_llm
# trends_pipeline: RunnableSequence = trends_prompt | trends_llm

# # ---------------------------
# # Pipeline Runner (Dynamic)
# # ---------------------------
# def run_pipeline(topic=None, symbol=None, query=None, limit_news=5, limit_stock=3, limit_trends=5):
#     """
#     Run pipelines dynamically based on the provided topic/entity/query.
#     Only fetches and processes the pipelines that have input.
#     """
#     logger.info("🚀 Running dynamic LangChain pipeline...")

#     try:
#         results = {}

#         # News pipeline
#         if topic:
#             news_items = fetch_news_helper(topic)
#             news_text = " ".join([i["text"] for i in news_items[:limit_news]]) if news_items else ""
#             if news_text:
#                 summary = news_pipeline.invoke({"text": news_text})
#                 results["news_summary"] = summary
#                 save_report("news", summary)

#         # Stock pipeline
#         if symbol:
#             stock_items = fetch_stock_helper(symbol)
#             stock_text = " ".join([i["text"] for i in stock_items[:limit_stock]]) if stock_items else ""
#             if stock_text:
#                 summary = stock_pipeline.invoke({"text": stock_text, "symbol": symbol})
#                 results["stock_summary"] = summary
#                 save_report("stock", summary)

#         # Trends / Search pipeline
#         if query:
#             trends_items = search_web_helper(query)
#             trends_text = " ".join([i["text"] for i in trends_items[:limit_trends]]) if trends_items else ""
#             if trends_text:
#                 summary = trends_pipeline.invoke({"text": trends_text, "query": query})
#                 results["trends_summary"] = summary
#                 save_report("trends", summary)

#         if not results:
#             logger.warning("⚠️ No input data provided for any pipeline")
#         else:
#             logger.info("✅ Pipeline execution completed")

#         return results

#     except Exception as e:
#         logger.error(f"❌ Pipeline execution failed: {e}")
#         raise

# # ---------------------------
# # Scheduler (Optional)
# # ---------------------------
# scheduler = BackgroundScheduler()
# scheduler.start()
# logger.info("⏰ Scheduler started (optional)")

import logging
import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from apscheduler.schedulers.background import BackgroundScheduler
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableLambda, RunnableSequence

from .db import async_engine, get_session
from .models import Report
from .fetch_helpers import fetch_news_helper, fetch_stock_helper, search_web_helper
from .utils.fallback_llm import generate_response_with_fallback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# Helper: Save report into DB (async)
# ---------------------------
async def save_report(kind: str, content: str):
    async with AsyncSession(async_engine) as session:
        report = Report(kind=kind, content=content)
        session.add(report)
        await session.commit()
        await session.refresh(report)
        logger.info(f"✅ Saved {kind} report at {report.created_at}")

# ---------------------------
# Prompt Templates
# ---------------------------
news_prompt = PromptTemplate.from_template(
    "Summarize the following news article:\n\n{text}"
)

stock_prompt = PromptTemplate.from_template(
    "Analyze the stock performance for {symbol} given this data:\n\n{text}"
)

trends_prompt = PromptTemplate.from_template(
    "Identify the main trends from the following search results:\n\n{text}"
)

# ---------------------------
# Runnable Wrappers
# ---------------------------
news_llm = RunnableLambda(lambda x: generate_response_with_fallback(x))
stock_llm = RunnableLambda(lambda x: generate_response_with_fallback(x))
trends_llm = RunnableLambda(lambda x: generate_response_with_fallback(x))

# ---------------------------
# Pipelines
# ---------------------------
news_pipeline: RunnableSequence = news_prompt | news_llm
stock_pipeline: RunnableSequence = stock_prompt | stock_llm
trends_pipeline: RunnableSequence = trends_prompt | trends_llm

# ---------------------------
# Pipeline Runner (Dynamic, async)
# ---------------------------
async def run_pipeline(topic=None, symbol=None, query=None, limit_news=5, limit_stock=3, limit_trends=5):
    """
    Run pipelines dynamically based on the provided topic/entity/query.
    Only fetches and processes the pipelines that have input.
    """
    logger.info("🚀 Running dynamic LangChain pipeline...")
    results = {}

    try:
        # News pipeline
        if topic:
            news_items = fetch_news_helper(topic)
            news_text = " ".join([i["text"] for i in news_items[:limit_news]]) if news_items else ""
            if news_text:
                summary = news_pipeline.invoke({"text": news_text})
                results["news_summary"] = summary
                await save_report("news", summary)

        # Stock pipeline
        if symbol:
            stock_items = fetch_stock_helper(symbol)
            stock_text = " ".join([i["text"] for i in stock_items[:limit_stock]]) if stock_items else ""
            if stock_text:
                summary = stock_pipeline.invoke({"text": stock_text, "symbol": symbol})
                results["stock_summary"] = summary
                await save_report("stock", summary)

        # Trends / Search pipeline
        if query:
            trends_items = search_web_helper(query)
            trends_text = " ".join([i["text"] for i in trends_items[:limit_trends]]) if trends_items else ""
            if trends_text:
                summary = trends_pipeline.invoke({"text": trends_text, "query": query})
                results["trends_summary"] = summary
                await save_report("trends", summary)

        if not results:
            logger.warning("⚠️ No input data provided for any pipeline")
        else:
            logger.info("✅ Pipeline execution completed")

        return results

    except Exception as e:
        logger.error(f"❌ Pipeline execution failed: {e}")
        raise

# ---------------------------
# Scheduler (Optional)
# ---------------------------
scheduler = BackgroundScheduler()
scheduler.start()
logger.info("⏰ Scheduler started (optional)")
