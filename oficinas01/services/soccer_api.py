from datetime import date
from time import time

from httpx import AsyncClient

from src.logger import logger

TODAY = date.today().strftime("%d-%m-%Y")

DELETED_KEYS = [
    "narration",
    "hasNarration",
    "statistic",
    "referee",
    "matchStatistics",
    "matchLink",
    "idMatch",
]


def format_user_response(data: dict) -> list[dict]:
    formmated_games = []
    for game in data:
        for key in DELETED_KEYS:
            del game[key]
        game["score"] = (
            str(game["homeTeam"]["score"]) + "-" + str(game["visitingTeam"]["score"])
        )
        game["homeTeam"] = game["homeTeam"]["name"]
        game["visitingTeam"] = game["visitingTeam"]["name"]
        game["tournament"] = game["tournament"]["tournament_name"]

        formmated_games.append(game)

    return formmated_games


async def get_soccer_games(client: AsyncClient) -> list[dict]:
    start_time = time()
    response = await client.get(
        f"https://www.cnnbrasil.com.br/wp-json/cnnbr/sports/soccer/v1/matches/date/{TODAY}",
    )

    data = response.json()

    games = format_user_response(data)[:15]

    end_time = time()
    elapsed_time = end_time - start_time

    logger.debug(f"Soccer API - Time elapsed: {elapsed_time:.2f} ms")

    return games
