import os
from fastapi import APIRouter
from app.database.db_operations import DB_operations as db
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from google import genai
from pathlib import Path

load_dotenv(dotenv_path=Path('./.env'))
app_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=app_key)

router = APIRouter()


async def fetch_news_url(news_id: int):
    try:
        query = "SELECT news_link from NewsItems where news_id = ?"
        params = (news_id,)
        res = await db.fetch_all_aysnc(query, params)
        return res[0][0]
    except Exception as e:
        print(f"Error in fetching news from db - {e}")

def scrape_article(url):
    print(f"scraping - {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/90.0.4430.212 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find the main article content
        article_text = ''

        # Common tags for articles
        for tag in ['article', 'main', 'div']:
            candidates = soup.find_all(tag)
            for candidate in candidates:
                # You can adjust heuristic: e.g., only select if it has a lot of text
                if len(candidate.text.strip()) > 500:
                    article_text = candidate.text.strip()
                    break
            if article_text:
                break

        # If still not found, fallback
        if not article_text:
            paragraphs = soup.find_all('p')
            article_text = '\n'.join([p.get_text() for p in paragraphs if p.get_text().strip()])

        return article_text.strip()

    except Exception as e:
        print(f"Error scraping article: {e}")
        return ""

def analyze_article(text):
    try:
        prompt = f"Summarize the following news article within 70 words. Also classify the political bias. Options are: Very Left, Left, Center, Right, Very Right, Not Applicable. Delimit using '|||||': \n\n{text}"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        
        response_text = response.text.strip()

        print(response_text)

        if '|||||' in response_text:
            return tuple(response_text.split("|||||"))

        else:
            return ("Summary isn't available at the moment. Please try later!","NA")

    except Exception as e:
        print(f"Error during summarization: {e}")
        return ("There was an issue summarizing the choosen article!","NA")


@router.get("/news/{news_id}/analyze")
async def get_news_analysis(news_id: int):
    # Fetch news from DB
    news_link = await fetch_news_url(news_id)
    article_text = scrape_article(news_link)
    print(article_text)
    summary, bias = analyze_article(article_text)
    return {"summary": summary, "bias": bias, "status":"Y"}