from datetime import datetime
from typing import Optional
from os import remove
from asyncio import sleep

from discord import TextChannel, Embed, Guild, Role, File
from discord.ext.commands import Cog, command, Context
from discord.ext.commands.core import has_role
from discord.member import Member
from discord.utils import get

from src.bot import Bot
from src.db.db import get_address
from src.qr.qr_make import create_qr_code
from src.api.axie_api import UserData
from SETUP import infinity_team_bot


class QRCode(Cog):
    def __init__(self, bot) -> None:
        self.bot: Bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("qr_code")

            self.guild: Guild = self.bot.get_guild(self.bot.guild_id)

            self.awaiting_chan: TextChannel = get(
                self.guild.channels, name=infinity_team_bot.awaiting_chan_name
            )
            self.alerts_channel: TextChannel = get(
                self.guild.channels, id=infinity_team_bot.alerts_channel
            )
            self.awaiting_role: Role = get(
                self.guild.roles, name=infinity_team_bot.awaiting_role_name
            )
            self.manager_role: Role = get(
                self.guild.roles, name=infinity_team_bot.manager_role_name
            )
            self.engine = self.bot.engine

    async def qr_expire_notify(self, member: Member):
        qr_expire_embed = Embed(
            title=f"{str(member)}'s QR has expired!",
            description=f"Use: ```{self.bot.PREFIX}info @{member.name}/{member.id}```\n```{self.bot.PREFIX}review @{member.name}/{member.id}```\n```{self.bot.PREFIX}qr @{member.name}/{member.id}```\n```{self.bot.PREFIX}disconnect @{member.name}/{member.id}```",
            timestamp=datetime.utcnow(),
        )
        qr_expire_embed.set_thumbnail(url=member.avatar_url)

        return await self.alerts_channel.send(
            embed=qr_expire_embed, content=f"{self.manager_role.mention}"
        )

    @has_role(infinity_team_bot.manager_role_name)
    @command(
        name="qr",
        brief="send an axie access qr code to the user, expires in 7 days.",
    )
    async def qr_code(self, ctx: Context, *, input_text: Optional[str]):
        # ? checking members
        if (not input_text) or (len(input_text) == 0):
            return await ctx.send(
                f"**You haven't provided a member.**\nUse `{self.bot.PREFIX}disconnect member(mention or id)`, make sure it's a user mention not a role mention."
            )
        input_list = input_text.split()

        try:
            member_id = int(input_list[0])
        except:
            try:
                member_id = int(input_list[0][3:-1])
            except:
                return await ctx.send("**Invalid User.**")
        member = get(self.guild.members, id=member_id)

        qr_file_name = await create_qr_code(
            discord_id=member.id, engine=self.engine
        )  # ? creating the qr code
        # print(qr_file_name, isfile(qr_file_name))  #!DEBUG
        if qr_file_name is None:
            return await ctx.send("**User doesn't have a Private Key.**")

        # ? send_qr_embed to user dms and admin channel
        qr_embed = Embed(
            title="Scholar QR Code",
            description=f"**User:** `{str(member)}`\n**Ronin Username:** `{await UserData.fetch_ronin_name(discord_id=member.id,engine=self.engine)}`\n**Ronin Address:** `ronin:{(get_address(discord_id=member.id,engine=self.engine))[2:]}`\n**This QR code expires in 7 days.**",
            timestamp=datetime.utcnow(),
        )
        qr_embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=qr_embed)  # ? admin
        await member.send(embed=qr_embed, file=File(qr_file_name))  # ? member

        remove(qr_file_name)  # ? deletes png from files after sending
        # print("start")  #!DEBUG
        await sleep(7 * 24 * 60 * 60)
        await self.qr_expire_notify(member)

        # self.bot.scheduler.add_job(
        #     lambda member=member: run(self.qr_expire_notify(member)),
        #     CronTrigger(second=20),  #!day=7),
        # )


def setup(bot):
    bot.add_cog(QRCode(bot))
