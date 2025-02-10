from dataclasses import asdict, dataclass
from time import time

import httpx
from bs4 import BeautifulSoup
from httpx import AsyncClient

from src.logger import logger


@dataclass
class BibleQuote:
    quote: str
    book: str
    interpretation: str


async def get_html(client: AsyncClient) -> str:
    response = await client.get("https://www.bibliaon.com/palavra_do_dia/")

    assert response.status_code == 200

    return response.text


async def get_bible_quote(client: AsyncClient) -> dict:
    start_time = time()
    html = await get_html(client)

    soup = BeautifulSoup(html, "html.parser")

    article = soup.find("div", {"class": "articlebody"})

    quote = article.find("blockquote").text.replace("\n", " ").strip()
    quote, book = quote.split("-", maxsplit=1)

    interpretation = article.find("blockquote").find_next_siblings("p")[:-1]
    interpretation = [p.text.replace("\n", " ").strip() for p in interpretation]
    interpretation = " ".join(interpretation)

    bible_quote = BibleQuote(quote, book, interpretation)

    end_time = time()
    elapsed_time = end_time - start_time

    logger.debug(f"Bible API - Time elapsed: {elapsed_time:.2f} ms")

    return asdict(bible_quote)


if __name__ == "__main__":
    import asyncio

    import httpx

    client = httpx.AsyncClient()

    asyncio.run(get_bible_quote(client))
