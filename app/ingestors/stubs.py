import httpx
import os
# from app.config import NEWSAPI_KEY, ALPHAVANTAGE_KEY, GOOGLE_API_KEY, GOOGLE_CX
NEWSAPI_KEY="8f2a0340180c473a808459bbe15f1164"
ALPHAVANTAGE_KEY="LQX9Y8VR0IVCQUK2"
GOOGLE_CX="72445796e54c84663"
GOOGLE_API_KEY="AIzaSyDkjEZkW5_tO_LmYsTJBKbNvzC8t6pnaDE"


# print(NEWSAPI_KEY)
# ------------------ NewsAPI ------------------
async def fetch_newsapi(query: str):
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "apiKey": NEWSAPI_KEY, "language": "en", "pageSize": 5}

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    articles = []
    for article in data.get("articles", []):
        articles.append({
            "title": article["title"],
            "url": article["url"],
            "content": article.get("description") or article.get("content")
        })
    return articles


# ------------------ Alpha Vantage ------------------
async def fetch_alpha_vantage(symbol: str):
    url = "https://www.alphavantage.co/query"
    params = {"function": "TIME_SERIES_DAILY", "symbol": symbol, "apikey": ALPHAVANTAGE_KEY}

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    time_series = data.get("Time Series (Daily)", {})
    prices = [
        {"date": date, "close": float(info["4. close"])}
        for date, info in time_series.items()
    ][:5]  # latest 5 days

    return {"symbol": symbol, "prices": prices}


# ------------------ Google CSE ------------------
async def fetch_google_cse(query: str):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title"),
                "url": item.get("link"),
                "snippet": item.get("snippet")
            })
        return results




# 4. Example usage
# import asyncio

# async def main():
#     news = await fetch_newsapi("AI markets")
#     stocks = await fetch_alpha_vantage("IBM")
#     search = await fetch_google_cse("autonomous AI agent")

#     print("NEWS:", news[:2])
#     print("STOCKS:", stocks)
#     print("SEARCH:", search[:2])

# asyncio.run(main())



# # Connectors are stubbed for MVP. Replace with real API calls.
# import httpx

# async def fetch_newsapi(query: str):
#     # TODO: use NEWSAPI_KEY; return list[dict]
#     # Return stub
#     return [{
#         "title": f"Stub News about {query}",
#         "url": "https://example.com/news",
#         "content": f"Sample content for query {query}."
#     }]

# async def fetch_alpha_vantage(symbol: str):
#     return {"symbol": symbol, "prices": [{"date": "2025-08-20", "close": 100.0}]}

# async def fetch_google_cse(query: str):
#     return [{
#         "title": f"Stub Web Result {query}",
#         "url": "https://example.com/search",
#         "snippet": f"Result for {query}"
#     }]
