from fastapi import APIRouter
from app.models import NewsItem, GetNewsByCategoryResponse, GetNewsByIdResponse, GetNewsCategoriesResponse
from app.database.db_operations import DB_operations as db
# from functools import cmp_to_key

router = APIRouter()

# def custom_sort(rec1, rec2):
#     if rec1[11] == 1:
#         return -1
#     else:
#         return 1


@router.get("/news")
async def get_news_by_category(
    category: str = "world",
    limit: int = 42,
    cursor: str | None = None,
    after_cursor: str | None = None 
    ):
    try:
        print(f"Get_news_by_category API called with: Category - {category}, Cursor - {cursor}, After Cursor - {after_cursor}")

        limit = min(limit, 100)

        if cursor:
            if not cursor.startswith("id_"):
                cursor = cursor.replace("T", " ")

        if not cursor:
            query = """
                SELECT news_id, news_link, news_title, news_author, news_published, news_tags, news_image_url, news_category, news_subcategory, website_name, news_lang, is_relevant
                FROM NewsItems 
                WHERE news_category = ? AND news_lang = 'en'
                ORDER BY news_published DESC,
                CASE WHEN
                news_lang = 'en' THEN 1 ELSE 2 END,
                news_id 
                LIMIT ?
            """
            params = (category, limit)

        elif cursor and not cursor.startswith("id_"):
            query = """
                SELECT news_id, news_link, news_title, news_author, news_published, news_tags, news_image_url, news_category, news_subcategory, website_name, news_lang, is_relevant
                FROM NewsItems 
                WHERE news_category = ? AND (news_published < ? OR news_published IS NULL) AND news_lang = 'en'
                ORDER BY news_published DESC,
                news_id 
                LIMIT ?
            """
            params = (category, cursor, limit)

        else:
            cursor = cursor[3:]
            query = """
                SELECT news_id, news_link, news_title, news_author, news_published, news_tags, news_image_url, news_category, news_subcategory, website_name, news_lang, is_relevant
                FROM NewsItems 
                WHERE news_category = ? AND news_id > ? AND news_published is null AND news_lang = 'en'
                ORDER BY
                news_id
                LIMIT ?
            """
            params = (category, cursor, limit)

        res = await db.fetch_all_aysnc(query, params)

        news_items: list[NewsItem]= []

        #res = sorted(res, key = cmp_to_key(custom_sort))

        news_items = [
            NewsItem(
            news_id = row[0],
            news_link=row[1],
            news_title=row[2],
            news_author=row[3],
            news_published=row[4],
            news_tags=row[5],
            news_image_url=row[6],
            news_category=row[7],
            news_subcategory=row[8],
            website_name=row[9],
            news_lang=row[10],
            is_relevant = row[11])
            for row in res
        ]

        next_cursor = news_items[-1].news_published.replace(" ", "T") if (news_items and news_items[-1] and news_items[-1].news_published) else None

        if not next_cursor:
            if len(news_items) == 0:
                next_cursor = None
            else:
                next_cursor = "id_" + str(max([news.news_id for news in news_items if not news.news_published]))
        
        print(next_cursor)

        return GetNewsByCategoryResponse(news=news_items, next_cursor=next_cursor)
    
    except Exception as e:
        print(f"Error in get_news_by_category - {e}")


@router.get("/news/categories")
async def get_news_categories():
    try:
        query = """SELECT DISTINCT news_category FROM NewsItems
                ORDER BY
                CASE WHEN news_category = 'world' THEN 1
                WHEN news_category = 'sports' THEN 2
                WHEN news_category = 'tech' THEN 3
                WHEN news_category = 'programming' THEN 4
                WHEN news_category = 'entertainment' THEN 5
                WHEN news_category = 'Business and finance' THEN 6
                WHEN news_category = 'science' THEN 7
                WHEN news_category = 'history' THEN 8
                ELSE 9 END
        """

        res = await db.fetch_all_aysnc(query)
        res = list(map(lambda x: x[0],res))

        resp = GetNewsCategoriesResponse(categories=res)        
        return resp
    
    except Exception as e:
        print(f"Error in get_news_categories - {e}")
        return []


@router.get("/news/id/{id}")
async def get_news_by_id(id: int):
    try:
        print(f"Get_news_by_id API called with: Id - {id}")

        if id:
            query = """
                SELECT news_id, news_link, news_title, news_author, news_published, news_tags, news_image_url, news_category, news_subcategory, website_name, news_lang
                FROM NewsItems 
                WHERE news_id = ? limit 1
            """
            params = (id,)

        res = await db.fetch_all_aysnc(query, params)

        news_items: list[NewsItem]= []

        news_items = [
            NewsItem(
            news_id = row[0],
            news_link=row[1],
            news_title=row[2],
            news_author=row[3],
            news_published=row[4],
            news_tags=row[5],
            news_image_url=row[6],
            news_category=row[7],
            news_subcategory=row[8],
            website_name=row[9],
            news_lang=row[10]) 
            for row in res
        ]

        return GetNewsByIdResponse(news=news_items)
    
    except Exception as e:
        print(f"Error in get_news_by_id - {e}")

