import httpx
from bs4 import BeautifulSoup


async def get_temperature_humidity():
    client = httpx.AsyncClient()
    response = await client.get(
        "https://www.simepar.br/simepar/forecast_by_counties/4106902"
    )

    soup = BeautifulSoup(response.text, "html.parser")

    assert response.status_code == 200

    temp = soup.find("span", {"class": "currentTemp"}).text.strip()
    humidity = (
        soup.find("span", {"class": "var"}, string="Umidade Relativa:")
        .find_next("span")
        .text
    ).strip()

    return {"temperature": temp, "humidity": humidity}


if __name__ == "__main__":
    import asyncio

    asyncio.run(get_temperature_humidity())
