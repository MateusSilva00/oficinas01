from dataclasses import asdict, dataclass

import pandas as pd
from dotenv import load_dotenv
from httpx import AsyncClient


@dataclass
class Stock:
    Date: str
    ChangeDay: float
    ChangeDayFormatted: str
    Change12M: float
    Change12MFormatted: str
    StockCode: str
    StockName: str
    Value: float
    ValueFormatted: str
    Volume: float
    VolumeFormatted: str


load_dotenv(override=True)

URL = "https://api.infomoney.com.br/ativos/top-alta-baixa-por-ativo/acao"


HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "DNT": "1",
    "If-None-Match": '"0e4669b3-e61a-4965-8b5e-b6ad7ff6619c"',
    "Origin": "https://www.infomoney.com.br",
    "Referer": "https://www.infomoney.com.br/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
}

PARAMS = {
    "sector": "Todos",
    "orderAtributte": "Volume",
    "pageIndex": "1",
    "pageSize": "15",
    "search": "",
}


async def get_market_trends(client: AsyncClient, is_winner=True) -> list[dict]:
    trend_type = "GAINERS" if is_winner else "LOSERS"

    response = await client.get(
        URL, follow_redirects=True, params=PARAMS, headers=HEADERS
    )

    assert response.status_code == 200

    data = response.json()
    stocks = []
    for item in data["Data"]:
        stocks.append(Stock(**item))

    stocks = [asdict(stock) for stock in stocks]

    return stocks


if __name__ == "__main__":
    import asyncio

    import httpx

    client = httpx.AsyncClient()

    async def main():
        trends = await get_market_trends(client)
        print(trends)

    asyncio.run(main())
