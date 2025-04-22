from pathlib import Path
from app.models import RssSource
import datetime as dt
import xml.etree.ElementTree as ET
from app.database.db_operations import DB_operations as db

class RssUrlLoader:

    @staticmethod
    async def load_rss_urls():
        try:
            
            print(f"Initiating database updation for RSS Urls at - {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Get the base resources folder
            # Ensure that the folder structure is YourMainFolder/resources/rssfeeds/FoldersWithCategorizedOPMLFiles for this to work
            resources_path = Path(__file__).resolve().parent.parent / "resources" / "rssfeeds"

            count = 0

            for category_folder in resources_path.iterdir():
                if category_folder.is_dir():
                    category = category_folder.name.capitalize()  # Folder name as category
                    
                    # Iterate through all OPML files in the category
                    for opml_file in category_folder.glob("*.opml"):
                        subcategory = opml_file.stem.capitalize()  # File name without extension

                        tree = ET.parse(opml_file, parser=ET.XMLParser(encoding="utf-8"))
                        root = tree.getroot()

                        # Find RSS feed URLs inside <outline> elements
                        for outline in root.findall(".//outline[@xmlUrl]"):
                            name = outline.attrib.get("title", "Unknown")  # Feed name
                            url = outline.attrib.get("xmlUrl")  # RSS URL

                            if url:
                                query = "INSERT INTO RssSources (news_category, news_subcategory, website_name, rss_url) values (?,?,?,?)"
                                params = (category, subcategory, name, url)
                                await db.execute_query_async(query,params)
                                count+=1

            print(f"{count} RSS Urls inserted in DB. Completed at - {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")            
                                    
        except Exception as e: 
            print(f"load_rss_urls Error - {e}")


    @staticmethod
    async def get_rss_source(retry_count : int = 1) -> list[tuple]:
        try:

            #I fixed it to 100 because processing all of them at once was overheating my mac
            # In a real world production setup, there could be a separate service with distributed setup to refresh data from rss feeds in the db

            One_time_fetch_limit = 100  

            query = "SELECT COUNT(*) FROM RssSources"
            count_rss_sources = await db.fetch_all_aysnc(query)

            if not count_rss_sources or not count_rss_sources[0] or count_rss_sources[0][0] == 0:
                print("Count of rss soruces = 0")
                await RssUrlLoader.load_rss_urls()

            query = "SELECT news_category, COUNT(news_category) FROM RssSources GROUP BY news_category;"
            category_counts = await db.fetch_all_aysnc(query)

            total_count = sum(count for _, count in category_counts)
            
            if total_count < One_time_fetch_limit:
                One_time_fetch_limit = total_count

            category_limits = dict()
            for catgeory, count in category_counts:
                category_limits[catgeory] = (count * One_time_fetch_limit) // total_count
                if category_limits[catgeory] == 0: category_limits[catgeory] = 1
            
            union_queries = []
            for category, limit in category_limits.items():
                query = f"""
                SELECT * FROM (
                SELECT news_category, news_subcategory, website_name, rss_url
                FROM RssSources WHERE news_category = '{category}'
                ORDER BY 
                RANDOM() LIMIT {limit}
                )
                """
                union_queries.append(query)

            final_sql_query = " UNION ALL ".join(union_queries) + ";"

            res_list = await db.fetch_all_aysnc(final_sql_query)

            # Delete the sources to ensure all of them are parsed once before filling them back
            cnt = 0
            for _,_,_,url in res_list:
                query = "DELETE FROM RssSources where rss_url = ?"
                params = (url,)
                if await db.execute_query_async(query,params):
                    cnt+=1

            print(f"{cnt} Rss sources deleted from db and being sent for parsing")

            return res_list
        
        except Exception as e:
            print(f"get_rss_source Error - {e}")
            return []