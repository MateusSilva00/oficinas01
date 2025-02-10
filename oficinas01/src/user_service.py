import httpx

from services.b3_api import get_market_trends
from services.bible_api import get_bible_quote
from services.news_api import get_news
from services.soccer_api import get_soccer_games
from src.database import get_db_connection

client = httpx.AsyncClient()


import asyncio


class UserService:
    async def get_user_services(self, user_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))

        user = cursor.fetchone()
        conn.close()

        if user:
            tasks = []

            if user["b3"]:
                tasks.append(get_market_trends(client, is_winner=True))
            else:
                tasks.append(None)

            if user["bible"]:
                tasks.append(get_bible_quote(client))
            else:
                tasks.append(None)

            if user["news"]:
                tasks.append(get_news(client))
            else:
                tasks.append(None)

            if user["soccer"]:
                tasks.append(get_soccer_games(client))
            else:
                tasks.append(None)

            results = await asyncio.gather(*tasks)

            return {
                "user_id": user["user_id"],
                "username": user["username"],
                "services": {
                    "B3": results[0],
                    "Bible": results[1],
                    "News": results[2],
                    "Soccer": results[3],
                },
            }

        return None
