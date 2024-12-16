# https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=087431a2a56b4d139f77b7af24a587bc
import os
from time import time

from dotenv import load_dotenv
from httpx import AsyncClient

from src.logger import logger

load_dotenv(override=True)


def format_user_response(data: dict):
    articles = data["articles"]
    news = [article for article in articles[:5]]

    formatted_news = []
    for new in news:
        del new["content"]
        new["source"] = new["source"]["name"]
        formatted_news.append(new)

    return formatted_news


async def get_news(client: AsyncClient) -> dict:
    start_time = time()
    querystring = {"country": "us", "category": "science"}

    response = await client.get(
        "https://newsapi.org/v2/top-headlines",
        headers={"X-Api-Key": os.environ["NEWS_API"]},
        params=querystring,
        follow_redirects=True,
    )

    assert response.status_code == 200

    data = response.json()
    news = format_user_response(data)

    end_time = time()
    elapsed_time = end_time - start_time

    logger.debug(f"News API - Time elapsed: {elapsed_time:.2f} ms")

    return news


if __name__ == "__main__":
    print(get_news())
