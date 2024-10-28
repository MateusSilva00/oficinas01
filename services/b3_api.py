import os

import httpx
import pandas as pd
from dotenv import load_dotenv

load_dotenv(override=True)

URL = "https://real-time-finance-data.p.rapidapi.com/market-trends"
headers = {
    "x-rapidapi-key": os.environ["B3_RAPID_API_KEY"],
    "x-rapidapi-host": "real-time-finance-data.p.rapidapi.com",
}

USECOLS = ["symbol", "name", "price", "change", "change_percent", "previous_close"]


def get_b3_trends(is_winner=True):
    trend_type = "GAINERS" if is_winner else "LOSERS"
    querystring = {"trend_type": trend_type, "country": "br", "language": "pt"}

    response = httpx.get(
        URL, headers=headers, params=querystring, follow_redirects=True
    )

    assert response.status_code == 200

    data = response.json()["data"]["trends"]

    dataframe = pd.DataFrame(data)
    dataframe = dataframe[dataframe["type"] == "stock"]

    dataframe.sort_values(by="change_percent", ascending=False, inplace=True)
    dataframe = dataframe[USECOLS]

    top_stocks = dataframe[:10]

    return top_stocks.to_dict("records")


if __name__ == "__main__":
    winners = get_b3_trends(is_winner=True)
    losers = get_b3_trends(is_winner=False)

    print(winners)
