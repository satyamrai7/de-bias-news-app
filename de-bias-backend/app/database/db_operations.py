import sqlite3
import aiosqlite

class DB_operations:

    dbpath = "database.db"

    # """Executes INSERT, UPDATE, DELETE queries."""
    # @staticmethod
    # def execute_query(query: str, params: tuple = ()) -> None:
    #     conn = sqlite3.connect(DB_operations.dbpath)
    #     try:
    #         cursor = conn.cursor()
    #         if params:
    #             cursor.execute(query, params)
    #         else:
    #             cursor.execute(query)
    #         conn.commit()
    #     except sqlite3.Error as e:
    #         print(f"Database Error: {e}")
    #     finally:
    #         conn.close()

    # """Executes SELECT and returns all rows."""
    # @staticmethod
    # def fetch_all(query: str, params: tuple = ()) -> list[tuple[any,...]]:
    #     conn = sqlite3.connect(DB_operations.dbpath)
    #     try:
    #         cursor = conn.cursor()
    #         if params:
    #             cursor.execute(query, params)
    #         else:
    #             cursor.execute(query)
    #         res = cursor.fetchall()
    #         return res # Returns list of tuples
    #     except sqlite3.Error as e:
    #         print(f"Database Error: {e}")
    #         return []
    #     finally:
    #         conn.close()


    """Executes INSERT, UPDATE, DELETE queries asynchronously"""
    @staticmethod
    async def execute_query_async(query: str, params: tuple = ()) -> bool:
        try:
            async with aiosqlite.connect(DB_operations.dbpath) as conn:
                if params:
                    await conn.execute(query, params)
                else:
                    await conn.execute(query)
                await conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            print(f"Query - {query} {params}")
            return False

    """Executes SELECT and returns all rows asynchronously"""
    @staticmethod
    async def fetch_all_aysnc(query: str, params: tuple = ()) -> list[tuple[any,...]]:
        try:
            async with aiosqlite.connect(DB_operations.dbpath) as conn:
                cursor = await conn.execute(query, params) if params else await conn.execute(query)
                res = await cursor.fetchall()
                return res  # Returns list of tuples
        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            print(f"Query - {query} {params}")
            return []
        
    @staticmethod
    async def create_schema():
        try:
            
            query = "DROP Table RssSources"
            await DB_operations.execute_query_async(query)

            query = """CREATE TABLE IF NOT EXISTS RssSources 
            (rss_url TEXT PRIMARY KEY COLLATE NOCASE, 
            news_category TEXT COLLATE NOCASE, 
            news_subcategory TEXT COLLATE NOCASE, 
            website_name TEXT COLLATE NOCASE)"""

            await DB_operations.execute_query_async(query)

            query = "CREATE INDEX IF NOT EXISTS idx_news_category_subcategory ON RssSources (news_category, news_subcategory)"
            await DB_operations.execute_query_async(query)

            query = """
            CREATE TABLE IF NOT EXISTS NewsItems (
                news_id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_link TEXT UNIQUE COLLATE NOCASE,
                news_title TEXT DEFAULT '' COLLATE NOCASE,
                news_author TEXT DEFAULT '' COLLATE NOCASE,
                news_published DATETIME NULL,
                news_tags TEXT DEFAULT '' COLLATE NOCASE,
                news_summary TEXT DEFAULT '' COLLATE NOCASE,
                news_image_url TEXT DEFAULT '' COLLATE NOCASE,
                news_category TEXT DEFAULT '' COLLATE NOCASE,
                news_subcategory TEXT DEFAULT '' COLLATE NOCASE,
                website_name TEXT DEFAULT '' COLLATE NOCASE,
                news_lang TEXT DEFAULT '' COLLATE NOCASE,
                dbtime DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_relevant int DEFAULT 0
            );
            """
            await DB_operations.execute_query_async(query)

            query = """
                CREATE INDEX IF NOT EXISTS idx_news_id_category
                ON NewsItems (news_id, news_category);
            """
            await DB_operations.execute_query_async(query)

            query = """
                CREATE INDEX IF NOT EXISTS idx_news_published_lang 
                ON NewsItems (news_published, news_lang);
            """

            await DB_operations.execute_query_async(query)

            query = """
                CREATE INDEX IF NOT EXISTS idx_is_relevant 
                ON NewsItems (is_relevant);
            """

            await DB_operations.execute_query_async(query)
            
        except Exception as e:
            print(f"Database error in create_schema - {e}")