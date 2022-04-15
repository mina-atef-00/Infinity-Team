from dataclasses import dataclass
from datetime import datetime, timedelta
from pprint import pprint
from typing import Optional, Union

from aiohttp import request
from src.db.db import check_user_exists, get_address, get_warns

"""
    test_address: 0x26d252724d08a30151ab5c87bd6b4fb5eadb1500
    endpoints:
        https://game-api.axie.technology/stats -> see how many calls to api

        https://game-api.axie.technology/slp/ronin_address
        https://game-api.axie.technology/mmr/ronin_address

        https://game-api.axie.technology/code -> shows how the token is processed
        https://game-api.axie.technology/player/ronin_address (req. auth) gets imp data

    def getslp(token,address):
        url=""
        headers={
        'Content-Type': "application/json",
        'Authorization':f'Bearer {token}'
        }
"""


@dataclass
class UserData:
    user_name: Optional[str] = None
    total_slp: Optional[int] = None
    total_claimable_slp: Optional[int] = None
    last_claim_date: Optional[datetime] = None
    avg_slp_per_day: Optional[float] = None

    warns_tup: Optional[tuple] = None
    ronin_address: Optional[str] = None

    mmr: Optional[int] = None
    rank: Optional[int] = None
    win_total: Optional[str] = None
    draw_total: Optional[str] = None
    lose_total: Optional[str] = None
    win_rate: Optional[str] = None

    @staticmethod
    async def fetch_grind_info(discord_id: int, engine, debug=False):

        if not check_user_exists(discord_id, engine):
            return None

        address = (
            get_address(discord_id, engine)
            if not debug
            else "0x26d252724d08a30151ab5c87bd6b4fb5eadb1500"
        )
        url = f"https://game-api.axie.technology/slp/{address}"

        # ? first slp call
        async with request(
            method="GET",
            url=url,
        ) as response:
            if response.status in (
                401,
                405,
                404,
            ):  #! 402->out of reqs, 401->wrong_token, 404->not_found
                return None

            elif 300 >= response.status >= 200:
                response_data = await response.json()

                user_data = UserData(
                    # ?from the first slp  call
                    total_slp=response_data[0]["total"],
                    total_claimable_slp=response_data[0]["claimable_total"],
                    last_claim_date=(
                        datetime.fromtimestamp(response_data[0]["last_claimed_item_at"])
                        + timedelta(days=14)
                    ).strftime(r"%a %m-%d-%Y"),
                    warns_tup=None
                    if get_warns(discord_id, engine) is None
                    else (
                        f"- {warn.reason} | `{warn.time.strftime(r'%a %m-%d-%Y')}`"
                        for warn in get_warns(discord_id, engine)
                    ),
                    ronin_address=address,
                )

        # ?second mmr call
        url = f"https://game-api.axie.technology/mmr/{address}"

        async with request(
            method="GET",
            url=url,
        ) as response:
            if response.status in (
                401,
                405,
                404,
            ):  #! 402->out of reqs, 401->wrong_token, 404->not_found
                return None

            elif 300 >= response.status >= 200:
                response_data = await response.json()

                # ?after the second mmr call
                user_data.user_name = response_data[0]["items"][1]["name"]
                user_data.mmr = response_data[0]["items"][1]["elo"]
                user_data.rank = response_data[0]["items"][1]["rank"]
                # user_data.win_total = response_data[0]["items"][1]["win_total"]
                # user_data.draw_total = response_data[0]["items"][1]["draw_total"]
                # user_data.lose_total = response_data[0]["items"][1]["lose_total"]

                # try:
                #     user_data.win_rate = str(
                #         int(user_data.win_total)
                #         / (
                #             int(user_data.win_total)
                #             + int(user_data.draw_total)
                #             + int(user_data.lose_total)
                #         )
                #     )
                # except:
                #     user_data.win_rate = "N/a"

        # ?third rapid api call
        url = f"https://axie-infinity.p.rapidapi.com/get-update/{address}"

        querystring = {"id": f"{address}"}
#TODO []
        headers = {
            "x-rapidapi-host": "axie-infinity.p.rapidapi.com",
            "x-rapidapi-key": "2b801ec6c6mshb7429daad787d97p1705f0jsn0a0e62d685ad",
        }

        async with request("GET", url, headers=headers, params=querystring) as response:
            if response.status in (
                401,
                405,
                404,
            ):  #! 402->out of reqs, 401->wrong_token, 404->not_found
                return None
            elif 300 >= response.status >= 200:
                response_data = await response.json()

            user_data.avg_slp_per_day = response_data["slp"]["average"]
            user_data.win_rate = response_data["leaderboard"]["winRate"]

        return user_data

    @staticmethod
    async def fetch_ronin_name(discord_id: int, engine):
        address = get_address(discord_id, engine)
        url = f"https://game-api.axie.technology/mmr/{address}"

        async with request(
            method="GET",
            url=url,
        ) as response:
            # print(response.status)  #!DEBUG
            # pprint(await response.text(), indent=4)  #!DEBUG
            if response.status in (
                401,
                405,
                404,
            ):  #! 402->out of reqs, 401->wrong_token, 404->not_found
                return None

            elif 300 >= response.status >= 200:
                response_data = await response.json()

                # ?after the second mmr call
                user_data = UserData(user_name=response_data[0]["items"][1]["name"])
                user_name = user_data.user_name
                return user_name


"""
https://api.lunaciaproxy.cloud/
https://api.axie.technology/getgenes/100001
https://api.axie.technology/getgenes/100001/all
https://api.axie.technology/getgenes/100001,767393
from SETUP import mystic_titans_bot
https://api.axie.technology/invalidateaxie/132714
https://api.axie.com.ph/get-axies/ronin****
"""
