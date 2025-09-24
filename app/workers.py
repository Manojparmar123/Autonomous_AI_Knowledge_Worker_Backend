import asyncio
import datetime
import json
from ingestors.stubs import fetch_newsapi, fetch_alpha_vantage, fetch_google_cse
from models import Document
from db import async_session, init_db
from enum import Enum
from datetime import datetime, timezone


async def run_news_job(query: str):
    articles = await fetch_newsapi(query)
    async with async_session() as session:
        for art in articles:
            doc = Document(
                source="newsapi",
                title=art["title"],
                url=art["url"],
                content=art["content"]
            )
            session.add(doc)
        await session.commit()

async def run_stock_job(symbol: str):
    stock_data = await fetch_alpha_vantage(symbol)
    async with async_session() as session:
        # doc = Document(
        #     source="alphavantage",
        #     title=f"Stock data for {symbol}",
        #     content=str(stock_data)
        # )
        doc = Document(
            source="alphavantage",
            title=f"Stock data for {symbol}",
            url=f"https://www.alphavantage.co/query?symbol={symbol}",  # ✅ fake but valid URL
            content=json.dumps(stock_data),
            # created_at=datetime.utcnow()
            created_at=datetime.now(timezone.utc)
        )
        session.add(doc)
        await session.commit()

async def run_google_job(query: str):
    results = await fetch_google_cse(query)
    async with async_session() as session:
        for res in results:
            doc = Document(
                source="google_cse",
                title=res["title"],
                url=res["url"],
                content=res["snippet"]
            )
            session.add(doc)
        await session.commit()







