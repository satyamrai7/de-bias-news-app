import aiohttp, asyncio, feedparser, re, datetime as dt, pytz, json
from langdetect import detect
from dateutil import parser as dateparser
from dateutil.tz import gettz
from app.models import NewsItem
from app.services.rss_url_loader import RssUrlLoader
from app.database.db_operations import DB_operations as db


############################# Currently not in use ######################################################

def normalize_text(text: str) -> str:
    """
    Normalize text by lowering case and replacing hyphens with spaces.
    """
    return text.lower().replace('-', ' ')


def is_news_relevant(title: str, summary: str) -> int:
    """
    Returns 1 if any keyword is found in title or summary, else 0.
    """

    keywords = {
        "election", "elections", "vote", "voting", "ballot", "polls", "campaign",
        "government", "regime", "parliament", "congress", "senate", "cabinet",
        "minister", "ministry", "president", "prime minister", "chancellor",
        "governor", "mayor", "geopolitics", "diplomacy", "foreign policy",
        "national security", "border", "territory", "sovereignty", "treaty",
        "sanctions", "UN", "NATO", "G7", "G20", "EU", "BRICS", "OPEC", "conflict",
        "war", "invasion", "airstrike", "missile", "terror", "terrorist", "military",
        "armed forces", "troops", "defense", "defence", "army", "navy", "coup",
        "rebellion", "protest", "uprising", "civil unrest", "martial law",
        "intelligence", "espionage", "spy", "The US", "strikes", "Israel", "Palestine", "Gaza", "West Bank", "U.S",
        "curfew", "unrest", "riot", "bomb", "missile", "Houthi", "Terrorism", "killed", "kill",
        "Market", "markets", "opposition"

        "Biden", "Trump", "Republican", "Democrat", "GOP", "Congress",
        "White House", "Capitol", "Senate", "House of Representatives", "Supreme Court",
        "SCOTUS", "DOJ", "FBI", "CIA", "IRS", "immigration", "2024 election", 
        "midterm", "presidential debate", "January 6", "gun control", "abortion",
        "border wall", "The US", "tarrif", "wall", "illegal", "immigrants", "mexico",
        "The USA", "USA", "U.S.A", "nuclear", "Iran",

        "Tories", "Labour", "Conservatives", "Brexit", "Downing Street",
        "House of Commons", "House of Lords", "Rishi Sunak", "Keir Starmer", "NHS",
        "Parliament", "Scotland", "Northern Ireland", "The UK", "UK",

        "BJP", "Congress", "AAP", "Shiv Sena", "DMK", "AIADMK", "Modi", "Rahul Gandhi", "Lok Sabha", "Rajya Sabha",
        "assembly elections", "CAA", "NRC", "Hindu", "Hindutva", "RSS", "ED", "CBI",
        "Delhi", "Kashmir", "Pakistan", "Reservation", "Language", "Caste", "elections",
        "election", "NEP", "UCC", "Muslim", "Islam", "Islamist", "WAQF", "Maoist", "Tribal", "Brahmin", "Dalit", "OBC",
        "Bangladesh", "Rohingya", "Kashmir", "India", "GDP",

        "Xi Jinping", "CCP", "Taiwan", "Hong Kong", "South China Sea", "Uighur", "Uyghur",
        "Xinjiang", "Censorship", "One China", "PLA", "Covid", "China",

        "Putin", "Zelenskyy", "Ukraine", "Crimea", "Donbas", "Moscow", "Kremlin",
        "NATO", "war", "sanctions", "invasion", "Kyiv",

        "abortion", "LGBTQ", "trans", "immigration", "gun rights", "climate change",
        "woke", "cancel culture", "CRT", "freedom of speech",

        "referendum", "autonomy", "dictatorship", "corruption", "authoritarian",
        "liberal", "conservative", "left-wing", "right-wing", "populist", "separatist",
        "opposition leader"
    }

    combined_text_list = normalize_text(f"{title} {summary}").split(" ")

    hits = 0
    for word in combined_text_list:
        if word in keywords:
            hits += 1
        if hits >= 3:
            return 1

    return 0

######################################################################################################


def extract_image_url(entry) -> str | None:
    #Extracts image URL from various possible sources in an RSS entry.

    # 1. Check media_content
    if hasattr(entry, "media_content"):
        for media in entry.media_content:
            if isinstance(media, dict) and "url" in media:
                return media["url"]

    # 2. Check enclosures
    if hasattr(entry, "enclosures"):
        for enclosure in entry.enclosures:
            if isinstance(enclosure, dict) and "url" in enclosure:
                return enclosure["url"]

    # 3. Check media_thumbnail
    if hasattr(entry, "media_thumbnail"):
        for thumbnail in entry.media_thumbnail:
            if isinstance(thumbnail, dict) and "url" in thumbnail:
                return thumbnail["url"]

    # 4. Extract image from content or summary using regex
    if hasattr(entry, "content"):
        for content in entry.content:
            img_match = re.search(r'<img.*?src="(.*?)".*?>', content.value)
            if img_match:
                return img_match.group(1)

    if hasattr(entry, "summary"):
        img_match = re.search(r'<img.*?src="(.*?)".*?>', entry.summary)
        if img_match:
            return img_match.group(1)

    return ""  # Return empty if no image found



async def fetch_news_from_rss_source(session: aiohttp.ClientSession, rss_source: tuple) -> list[NewsItem] | None:
    try:
        async with session.get(rss_source[3],timeout=5) as response:
            xml_data = await response.text()
            feed = feedparser.parse(xml_data)
            
            news_items = []

            for entry in feed.entries:
                news_title = entry.title if hasattr(entry, "title") else ""
                news_link = entry.link if hasattr(entry, "link") else ""
                news_published = entry.published if hasattr(entry, "published") else ""

                if news_published:
                    try:
                        tzinfos = {
                            "EST": gettz("America/New_York"),
                            "EDT": gettz("America/New_York"),
                            "PST": gettz("America/Los_Angeles"),
                            "PDT": gettz("America/Los_Angeles")
                        }
                        parsed_date = dateparser.parse(news_published, tzinfos=tzinfos)
                        if parsed_date:
                            news_published = parsed_date.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            news_published = None
                    except Exception as e:
                        news_published = None
                else:
                    news_published = None

                news_summary = entry.summary if hasattr(entry, "summary") else ""
                news_author = entry.author if hasattr(entry, "author") else ""
                news_tags = [tag.term for tag in entry.tags] if hasattr(entry, "tags") else []
                news_tags = json.dumps(news_tags)
                news_image_url = extract_image_url(entry)
                news_category = rss_source[0]
                news_subcategory = rss_source[1]
                website_name = rss_source[2]
                
                news_lang = ""
                try:
                    news_lang = detect(f"{news_title} {news_summary}")
                except:
                    news_lang = ""

                # is_relevant = is_news_relevant(news_title, news_summary)

                news_item = NewsItem(
                    news_title=news_title,
                    news_link=news_link,
                    news_published=news_published,
                    news_summary=news_summary,
                    news_author=news_author,
                    news_tags=news_tags,
                    news_image_url=news_image_url,
                    news_category = news_category,
                    news_subcategory = news_subcategory,
                    website_name = website_name,
                    news_lang=news_lang,
                    # is_relevant=is_relevant
                )
                news_items.append(news_item)
            
            return news_items

    except Exception as e:
        #print(f"Error in fetch_news_from_rss_source -> {e}")
        return None



async def load_news_in_db() -> None:
    try:

        rss_sources = await RssUrlLoader.get_rss_source()

        batch_size = 10

        if rss_sources:
            async with aiohttp.ClientSession() as session:
                for i in range(0,len(rss_sources),batch_size):
                    batch = rss_sources[i:i + batch_size]
                    tasks = [fetch_news_from_rss_source(session, rss_source) for rss_source in batch]
                    results = await asyncio.gather(*tasks)

                    all_news: list[NewsItem] = []

                    if results:
                        for newslist in results:
                            if newslist:
                                all_news.extend(newslist)
                    
                    #Insert Into DB
                    query = """
                        INSERT INTO NewsItems 
                        (news_link, news_title, news_author, news_published, news_tags, news_summary, news_image_url, news_category, news_subcategory, website_name, news_lang, dbtime, is_relevant)
                        Values
                        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT DO NOTHING;
                    """

                    cnt = 0
                    for news in all_news:
                        if news.news_link:
                            params = (news.news_link, news.news_title, news.news_author, news.news_published, news.news_tags, news.news_summary, news.news_image_url, news.news_category, news.news_subcategory, news.website_name, news.news_lang, dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0)
                            if await db.execute_query_async(query, params):
                                cnt+=1
                    print(f"{cnt} news articles inserted in db")

            cutoff_date = dt.datetime.now() - dt.timedelta(days=7)
            old_time = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:
        print(f"Error in rss_news_loader - {e}")


#Refreshes news every 10 mins
async def background_news_updater():
    while True:
        print(f"Background news updater started on - {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await load_news_in_db()
        print(f"Background news updater completed on - {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await asyncio.sleep(60)