from src.database import get_db_connection


class UserService:
    def get_user_services(self, user_id: int):
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
                    "B3": bool(user["b3"]),
                    "Bible": bool(user["bible"]),
                    "News": bool(user["news"]),
                    "Soccer": bool(user["soccer"]),
                },
            }

        return None
