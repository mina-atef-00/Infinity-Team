from datetime import datetime, timedelta
from typing import Optional

from discord import TextChannel, Embed, Guild, Member, Role, Message, Reaction, User
from discord.ext.commands import Cog, command, Context
from discord.ext.commands.core import has_permissions, has_role
from discord.utils import get

from SETUP import mystic_titans_bot
from src.db.db import (
    check_user_exists,
    connect_user_db,
    disconnect_user_db,
    add_warn_db,
    clr_warns,
    get_address,
)
from src.api.axie_api import UserData


class ScholarInfo(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    def send_member_address(self, member: Member) -> Embed:
        address = f"ronin:{(get_address(discord_id=member.id,engine=self.engine))[2:]}"

        member_address_embed = Embed(
            title="Member Ronin Address",
            description=f"{member.mention}\n```{address}```",
        )
        member_address_embed.set_thumbnail(url=member.avatar_url)
        return member_address_embed

    def send_role_members_addresses(self, role: Role) -> Embed:
        role_members_gen = (member for member in role.members)
        members_address_format_txt = "\n".join(
            [
                f"{str(mmbr)} | `ronin:{(get_address(discord_id=mmbr.id,engine=self.engine))[2:]}`"
                for mmbr in role_members_gen
            ]
        )

        members_address_embed = Embed(
            title="Members Ronin Addresses", description=members_address_format_txt
        )
        return members_address_embed

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("scholar_info")

            self.guild: Guild = self.bot.get_guild(self.bot.guild_id)

            self.awaiting_chan: TextChannel = get(
                self.guild.channels, name=mystic_titans_bot.awaiting_chan_name
            )
            self.alerts_channel: TextChannel = get(
                self.guild.channels, id=mystic_titans_bot.alerts_channel
            )

            self.awaiting_role: Role = get(
                self.guild.roles, name=mystic_titans_bot.awaiting_role_name
            )
            self.manager_role: Role = get(
                self.guild.roles, name=mystic_titans_bot.manager_role_name
            )
            self.engine = self.bot.engine
            # print(self.engine)  #!DEBUG

    @has_role(mystic_titans_bot.manager_role_name)
    @command(
        name="review",
        brief=f"gets info on earnings of a user, and their warnings\n```review member(mention/id)```",
    )
    async def review_user(self, ctx: Context, *, input_text: Optional[str]):

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
        member: Member = get(self.guild.members, id=member_id)

        member_data: UserData = await UserData.fetch_grind_info(
            discord_id=member.id, engine=self.engine
        )
        if member_data is None:
            return await ctx.send("**User is not in Database.**")

        else:
            member_info_embed = Embed(
                title="User Info", description=f"**User:** {member.mention}\n"
            )
            member_info_embed.set_thumbnail(url=member.avatar_url)

            fields_ = (
                ("👤User", member_data.user_name, True),
                ("📍Ronin Address", f"`ronin:{(member_data.ronin_address)[2:]}`", False),
                ("⚔️MMR", member_data.mmr, True),
                ("🏆Rank", member_data.rank, True),
                (
                    "Total SLP",
                    f"<:slp:901571980011139173>{member_data.total_slp}",
                    True,
                ),
                (
                    "Average SLP/day",
                    f"<:slp:901571980011139173>{member_data.avg_slp_per_day}",
                    True,
                ),
                ("🧬Win Rate", f"`{member_data.win_rate}%`", True),
                (
                    "🕑Next Claim date",
                    f"`{member_data.last_claim_date}`",
                    False,
                ),
                # ("🗡️Wins", member_data.win_total, True),
                # ("🛡️Draws", member_data.draw_total, True),
                # ("💔Losses", member_data.lose_total, True),
                (
                    "Warnings",
                    "`User has no warnings.`"
                    if member_data.warns_tup is None
                    else "\n".join(member_data.warns_tup),
                    False,
                ),
            )
            for name, val, inline in fields_:
                member_info_embed.add_field(name=name, value=val, inline=inline)

            return await ctx.send(embed=member_info_embed)

    @has_role(mystic_titans_bot.manager_role_name)
    @command(
        name="info",
        brief=f"shows user's ronin address, or the ronin addresses of users with a certain role\n```info member(mention/id)```",
    )
    async def user_info(self, ctx: Context, *, input_text: Optional[str]):
        # print(input_list)  #!DEBUG

        if (not input_text) or (len(input_text) == 0):
            return await ctx.send(
                f"**You haven't provided a user or a role.**\nUse `{self.bot.PREFIX}info member(mention or id)/role(mention or id)`"
            )
        input_list = input_text.split()

        # ?checking mentions
        if input_list[0].startswith("<"):
            if input_list[0][2] == "!":  # ?member
                try:
                    member_id = int(input_list[0][3:-1])
                    member: Member = get(self.guild.members, id=member_id)
                    # print("pass member_mention")  #!DEBUG
                    # print(member_id, member)  #!DEBUG
                    return await ctx.send(embed=self.send_member_address(member=member))

                except:
                    return await ctx.send("**Invalid User.**")


            elif input_list[0][2] == "&":  # ?role
                try:
                    role_id = int(input_list[0][3:-1])
                    role: Role = get(self.guild.roles, id=role_id)
                    # print("pass role_mention")  #!DEBUG
                    # print(role_id, role)  #!DEBUG
                    return await ctx.send(
                        embed=self.send_role_members_addresses(role=role)
                    )

                except:
                    return await ctx.send("**Invalid user/role.**")

        # ? checking ids
        else:
            # ?checking member_id
            try:
                member_id = int(input_list[0])
                member: Member = get(self.guild.members, id=member_id)
                # print("pass member_id")  #!DEBUG
                return await ctx.send(embed=self.send_member_address(member=member))

            except:
                # ?checking role_id
                try:
                    # print("fail member_id")  #!DEBUG
                    role_id = int(input_list[0])
                    role: Role = get(self.guild.roles, id=role_id)
                    # print("pass role_id")  #!DEBUG
                    return await ctx.send(
                        embed=self.send_role_members_addresses(role=role)
                    )

                except:
                    return await ctx.send("**Invalid user/role ID.**")


def setup(bot):
    bot.add_cog(ScholarInfo(bot))
