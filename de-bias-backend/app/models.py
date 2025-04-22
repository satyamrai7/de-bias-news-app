from pydantic import BaseModel

class NewsItem(BaseModel):
    news_id: int = 0
    news_title: str = ""
    news_author: str = ""
    news_link: str = ""
    news_published: str | None = None
    news_tags: str = []
    news_summary: str = ""
    news_image_url: str = ""
    news_category: str = ""
    news_subcategory: str = ""
    website_name: str = ""
    news_lang: str = ""
    is_relevant: int = 0

class RssSource(BaseModel):
    news_category: str = 0
    news_subcategory: str = 0
    website_name: str = 0
    rss_url: str = 0


class GetNewsByCategoryResponse(BaseModel):
    news: list[NewsItem] | list
    next_cursor: str | None


class GetNewsByIdResponse(BaseModel):
    news: list[NewsItem] | list


class GetNewsCategoriesResponse(BaseModel):
    categories: list[str] | list