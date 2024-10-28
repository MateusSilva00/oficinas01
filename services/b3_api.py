import os

import pandas as pd
from dotenv import load_dotenv
from httpx import AsyncClient

load_dotenv(override=True)

URL = "https://real-time-finance-data.p.rapidapi.com/market-trends"
headers = {
    "x-rapidapi-key": os.environ["B3_RAPID_API_KEY"],
    "x-rapidapi-host": "real-time-finance-data.p.rapidapi.com",
}

USE_B3_COLS = ["symbol", "name", "price", "change", "change_percent", "previous_close"]
USE_CRYPTO_COLS = ["currency", "exchange_rate", "previous_close", "last_update_utc"]


def get_b3_trends(data: dict) -> dict:
    dataframe = pd.DataFrame(data)
    dataframe = dataframe[dataframe["type"] == "stock"]

    dataframe.sort_values(by="change_percent", ascending=False, inplace=True)
    dataframe = dataframe[USE_B3_COLS]

    top_stocks = dataframe[:10]

    return top_stocks.to_dict("records")


async def get_cripto_trends(client: AsyncClient, trend_type: str = "CRYPTO") -> dict:
    querystring = {"trend_type": trend_type, "country": "br", "language": "pt"}

    response = await client.get(
        URL, headers=headers, params=querystring, follow_redirects=True
    )
    assert response.status_code == 200

    data = response.json()["data"]["trends"]
    df = pd.DataFrame(data[:5])
    df["currency"] = df["from_symbol"] + "/" + df["to_symbol"]
    df = df[USE_CRYPTO_COLS]

    return df.to_dict("records")


async def get_market_trends(client: AsyncClient, is_winner=True) -> dict:
    trend_type = "GAINERS" if is_winner else "LOSERS"
    querystring = {"trend_type": trend_type, "country": "br", "language": "pt"}

    response = await client.get(
        URL, headers=headers, params=querystring, follow_redirects=True
    )

    assert response.status_code == 200

    data = response.json()["data"]["trends"]

    if not len(data):
        return await get_cripto_trends(client)

    return get_b3_trends(data)


if __name__ == "__main__":
    winners = get_market_trends(is_winner=True)
    losers = get_market_trends(is_winner=False)

    print(winners)
