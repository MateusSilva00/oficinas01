import httpx

from services.b3_api import get_b3_trends
from services.bible_api import get_bible_quote
from services.news_api import get_news
from services.soccer_api import get_soccer_games
from src.database import get_db_connection

client = httpx.AsyncClient()


class UserService:
    async def get_user_services(self, user_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))

        user = cursor.fetchone()
        conn.close()

        if user:
            return {
                "user_id": user["user_id"],
                "username": user["username"],
                "services": {
                    "B3": (
                        await get_b3_trends(client, is_winner=True)
                        if user["b3"]
                        else None
                    ),
                    "Bible": await get_bible_quote(client) if user["bible"] else None,
                    "News": await get_news(client) if user["news"] else None,
                    "Soccer": (
                        await get_soccer_games(client) if user["soccer"] else None
                    ),
                },
            }

        return None
