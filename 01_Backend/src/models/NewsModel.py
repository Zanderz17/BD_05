from database.db import get_connection
from .entities.NewsArticle import NewsArticle


class NewsModel():
    #########################################################
    @classmethod  # Decorator -> To use without instance a object
    def get_news_query(self, query, top_k):
        try:
            connection = get_connection()
            NewsArray = []

            with connection.cursor() as cursor:
                cursor.execute(
                    f"""SELECT id_, title, ts_rank_cd(search_txt, query) AS score
                        FROM json_to_pos, phraseto_tsquery('english','{query}') query
                        WHERE query @@ search_txt
                        ORDER BY score DESC
                        LIMIT {top_k};""")
                resulset = cursor.fetchall()
                for row in resulset:
                    NewsItem = NewsArticle(row[0], row[1], row[2])
                    NewsArray.append(NewsItem.to_JSON())

            connection.close()
            return NewsArray

        except Exception as ex:
            raise Exception(ex)
