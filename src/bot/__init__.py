from discord import Intents, Embed, Message
from discord.activity import Game
from discord.enums import Status
from discord.ext.commands import Bot as BotBase, CommandNotFound
from discord.ext.commands.errors import (
    BadArgument,
    CommandOnCooldown,
    MissingRequiredArgument,
    MissingRole,
    MissingPermissions,
    BotMissingPermissions,
    NoPrivateMessage,
)
from discord.errors import HTTPException, Forbidden

from apscheduler.schedulers.asyncio import (
    AsyncIOScheduler,
)
from asyncio.tasks import sleep
from datetime import datetime
from glob import glob
from SETUP import infinity_team_bot
from src.db.db import connect_to_db

PREFIX = infinity_team_bot.prefix
OWNER_ID = infinity_team_bot.bot_owner_user_id
COGS = [path.split("/")[-1][:-3] for path in glob("./src/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument, MissingRequiredArgument)


class Ready(object):
    def __init__(self) -> None:
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"    -{cog} cog ready")

    def all_ready(self):
        print("Cogs stuff started/finished")
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.guild_id = infinity_team_bot.server_id

        self.scheduler = AsyncIOScheduler()
        self.ready = False
        self.cogs_ready = Ready()
        self.TOKEN = infinity_team_bot.token
        super().__init__(
            command_prefix=PREFIX,
            OWNER_ID=OWNER_ID,
            intents=Intents.all(),
            member=True,
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"src.cogs.{cog}")

    def run(self):
        self.setup()
        print("Running Bot...")
        super().run(self.TOKEN)

    async def on_connect(self):
        print("Bot Connected")

        game = Game(f"{self.PREFIX}")
        await self.change_presence(status=Status.idle, activity=game)

    async def on_disconnect(self):
        print("Bot Disconnected, Reconnecting...")

    async def on_error(self, event_method, *args):
        if event_method == "on_command_error":
            await args[0].send("Something went wrong")
        raise

    async def on_command_error(self, context, exception):
        if any([isinstance(exception, err) for err in IGNORE_EXCEPTIONS]):
            pass

        elif isinstance(exception, CommandOnCooldown):
            await context.send(
                f"**Command is on {str(exception.cooldown.type).split('.')[-1]} Cooldown!**\nWait for {exception.retry_after:,.1f}s."
            )  # ? cooldown seconds are formatted to one floating point

        elif isinstance(exception, BadArgument):
            await context.send("**You wrote a wrong command!**")

        elif isinstance(exception, HTTPException):
            await context.send("**Can't send message**")
            raise exception

        elif isinstance(exception, Forbidden):
            await context.send("**Forbidden! I can't do that.**")

        elif isinstance(exception, MissingRequiredArgument):
            await context.send(
                "**There's an argument missing in the command you've sent!**"
            )

        elif isinstance(exception, MissingRole):
            missing_role_embed = Embed(
                title="Looks like you're missing a role.",
                description=f"Please contact the mods.",
                colour=0x4AD26F,
            )

            await context.send(embed=missing_role_embed)

        elif isinstance(exception, MissingPermissions):
            await context.send("**You don't have permission to do that!**")

        elif isinstance(exception, BotMissingPermissions):
            await context.send(
                f"**I don't have** `{' '.join(exception.missing_perms)}` **permissions.**"
            )

        elif isinstance(exception, NoPrivateMessage):
            await context.send(
                "**You can't use this command on DMs.**\nPlease use on server."
            )

        elif hasattr(exception, "original"):
            raise exception

        else:
            raise exception

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(infinity_team_bot.server_id)
            self.alerts_channel = self.get_channel(infinity_team_bot.alerts_channel)
            self.engine = connect_to_db()

            # self.scheduler.start()
            ready_txt = f"{infinity_team_bot.bot_name} Bot Ready @ {(datetime.now()).strftime(r'%I:%M:%S %p | %d-%b-%y')}"

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print(ready_txt)

            testing_embed = Embed(
                title=f"{infinity_team_bot.bot_name} bot is Online!",
                description=f"Call me on `{self.PREFIX}`",
                colour=0xED9D12,
                timestamp=datetime.now(),
            )

            await self.alerts_channel.send(embed=testing_embed)

        else:
            print("Bot Reconnected")

    async def on_message(self, message: Message):
        await self.process_commands(message)


bot = Bot()
