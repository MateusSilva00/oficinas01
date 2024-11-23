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

URL = "https://api.infomoney.com.br/markets/high-low/b3"

USE_B3_COLS = ["symbol", "name", "price", "change", "change_percent", "previous_close"]
USE_CRYPTO_COLS = ["currency", "exchange_rate", "previous_close", "last_update_utc"]

PARAMS = {
    "sector": "Todos",
    "orderAtributte": "High",
    "pageIndex": "1",
    "pageSize": "15",
    "type": "json",
}


def get_b3_trends(data: dict) -> dict:
    dataframe = pd.DataFrame(data)
    dataframe = dataframe[dataframe["type"] == "stock"]

    dataframe.sort_values(by="change_percent", ascending=False, inplace=True)
    dataframe = dataframe[USE_B3_COLS]

    top_stocks = dataframe[:5]

    return top_stocks.to_dict("records")


async def get_market_trends(client: AsyncClient, is_winner=True) -> list[dict]:
    trend_type = "GAINERS" if is_winner else "LOSERS"

    response = await client.get(URL, follow_redirects=True)

    assert response.status_code == 200

    data = response.json()
    date = data["ReferenceDate"]

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
