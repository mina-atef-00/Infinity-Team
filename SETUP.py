### Some Notes ###


from dataclasses import dataclass
from datetime import timedelta


@dataclass
class MysticTitans:

    # ? Bot Name
    bot_name: str

    # ?  bot token
    token: str

    # ?  prefix that is before commands, like (!) for rhythm (!play)
    prefix: str

    # ?  the bot owner's user id (right click/hold on user and search for copy id after enabling developer options)
    bot_owner_user_id: int

    # ?  the server id where the bot will work on (it can be found the same way as the owner id)
    server_id: int

    # ?  bot technical messages channel id (get it like the owner and server)
    alerts_channel: int

    # ?  bot invite link to server
    invite_link: str

    # ? awaiting channel name
    awaiting_chan_name: str

    # ? awaiting team role name
    awaiting_role_name: str

    # ? manager_role_name: str
    manager_role_name: str


#! CHANGE THE CONFIGURATION HERE
mystic_titans_bot = MysticTitans(
    token="ODk3MTcwMzk3MzkxMzY0MTI2.YWRxCw.f5kE0f_xFoCM_zibDb-ATZfXWXE",  #! change it
    prefix="!",
    bot_name="Mystic Titans",
    awaiting_chan_name="Mystic Titans",
    awaiting_role_name="Giants Awaiting Team",
    manager_role_name="Manager",
    ############################################################ #? More Technical
    bot_owner_user_id=553825865163735042,  #! set to @tiecubed
    server_id=897160657345060986,  #! change it to your server id
    alerts_channel=897160657345060990,  #! change it to the alerts channel id
    invite_link=(
        r"https://discord.com/api/oauth2/authorize?client_id=890552186394791957&permissions=8&redirect_uri=https%3A%2F%2Fdiscord.com%2Fapi%2Foauth2%2Fauthorize%3Fclient_id%3D890552186394791957%26permissions%3D8%26redirect_uri%3Dhttps%253A%252F%252Fdiscord.com%252Fapi%252Foauth2%252Fauthorize%253Fclient_id%253D890552&scope=bot",
    ),
)

# <====================================================================>

