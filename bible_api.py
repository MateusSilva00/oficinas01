import requests
import json

URL = "https://bolls.life/get-random-verse/NVT"


def format_user_response(data: dict) -> str:
    return (
        (
            data["book"]
            + " "
            + str(data["chapter"])
            + ":"
            + str(data["verse"])
            + " "
            + data["text"]
        )
        .replace("\n", " ")
        .replace("<br>", " ")
    )


def get_bible_quote():
    response = requests.get(URL)

    assert response.status_code == 200

    data = response.json()

    book = str(data["book"])
    bible_order = json.load(open("bible_order.json"))

    del data["pk"]
    del data["translation"]
    data["book"] = bible_order[book]["Nome"]
    data["book_abbr"] = bible_order[book]["Abreviação"]
    data["user_response"] = format_user_response(data)

    return data


if __name__ == "__main__":
    print(get_bible_quote())
