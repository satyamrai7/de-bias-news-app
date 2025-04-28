from fastapi import APIRouter
from app.database.db_operations import DB_operations as db
#from transformers import pipeline
from bs4 import BeautifulSoup
import requests
from google import genai


client = genai.Client(api_key="TEST_API_KEY")


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

def summarize_article(text):
    return "I am batman"
    try:
        prompt = f"Summarize the following news article in 5-6 sentences:\n\n{text}"

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"Summarize the following news article in 5-6 sentences:\n\n{text}")
        return response.text.strip()
    except Exception as e:
        print(f"Error during summarization: {e}")
        return "Error summarizing the article."


def classify_bias(text):
    try:
        prompt = "Classify the political bias of the following news article. Options are: Very Left, Left, Center, Right, Very Right, Not Applicable. Only output one of these options and no extra words.\n\n" + text
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error during bias classification: {e}")
        return "Not Applicable"


@router.get("/news/{news_id}/analyze")
async def get_news_analysis(news_id: int):
    # Fetch news from DB
    news_link = await fetch_news_url(news_id)
    print(news_link)
    article_text = scrape_article(news_link)
    summary = summarize_article(article_text)
    bias = classify_bias(article_text)
    return {"summary": summary, "bias": bias}
