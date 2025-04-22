from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import news
from app.services.rss_url_loader import RssUrlLoader
from datetime import datetime
from app.database.db_operations import DB_operations as db
from contextlib import asynccontextmanager
from app.services.rss_news_loader import background_news_updater
import requests, aiohttp, asyncio

# async def poc():
    # response = requests.get("https://example.com")
    # html = response.text
    # print(html)
    # session = requests.session()
    # response = session.get("https://www.example.com")
    # html = response.text
    # print(html)
    # async with aiohttp.ClientSession() as session:
    #     async with session.get("https://www.example.com") as response:
    #         print(await response.text())    
    # query = "DELETE FROM NewsItems"
    # await db.execute_query_async(query)
    # query = "SELECT news_category, COUNT(news_category) FROM RssSources GROUP BY news_category"
    # print(await db.fetch_all_aysnc(query))
    # query = """
    #         SELECT * FROM NewsItems 
    #         WHERE news_category = ? AND news_published < ? 
    #         ORDER BY CASE WHEN
    #         news_lang = 'en' THEN 1 ELSE 2 END,
    #         news_published DESC, news_lang 
    #         LIMIT ?
    #     """
    # params = ('world', '2025-03-23 13:04:14', 10)
    # print(await db.fetch_all_aysnc(query, params))


@asynccontextmanager
async def lifespan(app: FastAPI):

    print(f"Application startup at - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await db.create_schema()
    print(f"Schema creation completed at - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await RssUrlLoader.load_rss_urls()
    print(f"RSS URL Loader completed at - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    asyncio.create_task(background_news_updater())
    yield

    print(f"Application ended at - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# Define FastAPI instance app
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend dev URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the news API routes
app.include_router(news.router)


@app.get("/")
async def greet():
    return {
        "message": "hello"
    }