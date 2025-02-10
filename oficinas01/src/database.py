import sqlite3
from contextlib import closing

from src.logger import logger

DB_NAME = "test.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        with closing(conn.cursor()) as cursor:
            logger.debug("Initializing database...")
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                b3 BOOLEAN NOT NULL DEFAULT 0,
                bible BOOLEAN NOT NULL DEFAULT 0,
                news BOOLEAN NOT NULL DEFAULT 0,
                soccer BOOLEAN NOT NULL DEFAULT 0,
                yaml_face TEXT
            )
            """
            )

            cursor.execute("SELECT COUNT(*) FROM users")

            logger.debug("Database initialized.")

            logger.debug("Populating database...")
            if cursor.fetchone()[0] == 0:
                cursor.executemany(
                    """
                INSERT INTO users (username, b3, bible, news, soccer)
                VALUES (?, ?, ?, ?, ?)
                """,
                    [
                        (
                            "Wiu Chakur",
                            True,
                            True,
                            True,
                            True,
                        ),
                        (
                            "Lucas",
                            False,
                            True,
                            True,
                            True,
                        ),  # Usuário 2 com Bible, News e Soccer
                        (
                            "Chaves Anarcocapilista",
                            False,
                            False,
                            False,
                            True,
                        ),  # Usuário 3 apenas com Soccer
                    ],
                )
            logger.debug("Database populated")
            conn.commit()


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
