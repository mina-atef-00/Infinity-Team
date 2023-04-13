from dataclasses import dataclass
import os
import dotenv

dotenv.load_dotenv(".env")


@dataclass
class InfinityTeam:
    bot_name: str
    token: str
    prefix: str
    bot_owner_user_id: int
    server_id: int
    alerts_channel: int
    invite_link: str
    awaiting_chan_name: str
    awaiting_role_name: str
    manager_role_name: str


# ! CHANGE THE CONFIGURATION HERE
infinity_team_bot = InfinityTeam(
    token=str(os.getenv("token")),
    prefix=str(os.getenv("prefix")),
    bot_name=str(os.getenv("bot_name")),
    awaiting_chan_name=str(os.getenv("awaiting_chan_name")),
    awaiting_role_name=str(os.getenv("awaiting_role_name")),
    manager_role_name=str(os.getenv("manager_role_name")),
    bot_owner_user_id=int(os.getenv("bot_owner_user_id", "0")),
    server_id=int(os.getenv("server_id", "0")),
    alerts_channel=int(os.getenv("alerts_channel", "0")),
    invite_link=str(os.getenv("invite_link")),
)
