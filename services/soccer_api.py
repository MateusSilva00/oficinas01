from datetime import date

import httpx

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


def get_soccer_games() -> list[dict]:
    response = httpx.get(
        f"https://www.cnnbrasil.com.br/wp-json/cnnbr/sports/soccer/v1/matches/date/{TODAY}",
    )

    data = response.json()

    games = format_user_response(data)

    return games


if __name__ == "__main__":
    print(get_soccer_games())
