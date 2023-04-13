from datetime import datetime
from typing import Optional
from src.bot import Bot

from discord import (
    TextChannel,
    Embed,
    Guild,
    Member,
    Role,
    Message,
    Reaction,
    User,
)
from discord.ext.commands import Cog, command, Context
from discord.ext.commands.core import has_role
from discord.utils import get

from SETUP import infinity_team_bot
from src.db.db import (
    connect_user_db,
    disconnect_user_db,
    add_warn_db,
)


class ManageScholars(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("manage_scholars")

            self.guild: Guild = self.bot.get_guild(self.bot.guild_id)

            self.awaiting_chan = get(
                self.guild.channels, name=infinity_team_bot.awaiting_chan_name
            )
            self.alerts_channel = get(
                self.guild.channels, id=infinity_team_bot.alerts_channel
            )
            self.awaiting_role = get(
                self.guild.roles, name=infinity_team_bot.awaiting_role_name
            )
            self.manager_role = get(
                self.guild.roles, name=infinity_team_bot.manager_role_name
            )
            self.engine = self.bot.engine
            # print(self.engine)  #!DEBUG

    @Cog.listener()
    async def on_member_join(self, member: Member):
        await member.add_roles(self.awaiting_role)

        member_join_embed = Embed(
            title="Member Joined",
            description=f"{member.mention}\nID: `{str(member.id)}`",
            colour=member.colour,
            timestamp=datetime.utcnow(),
        )
        await self.alerts_channel.send(embed=member_join_embed)

    @has_role(infinity_team_bot.manager_role_name)  # TODO ADD QR CODE TO USER
    @command(
        name="connect",
        brief="connects a user to a specific ronin address\n```connect member(mention/id) ronin:address 0xprivate_key(optional)```",
    )
    async def connect_user(
        self,
        ctx: Context,
        *,
        input_text: Optional[str],
    ):
        if (not input_text) or (len(input_text) == 0):
            return await ctx.send(
                f"**You haven't provided a member or a ronin address or a private key.**\nUse `{self.bot.PREFIX}connect member_mention(or id) ronin_address private_key`, make sure it's a user mention not a role mention."
            )
        input_list = input_text.split()
        if len(input_list) < 2:
            return await ctx.send(
                f"**You haven't provided a member or a ronin address or a private key.**\nUse `{self.bot.PREFIX}connect member_mention(or id) ronin_address private_key`, make sure it's a user mention not a role mention."
            )

        try:
            member_id = int(input_list[0])
        except Exception:
            member_id = int(input_list[0][3:-1])

        member, ronin_address = (
            get(self.guild.members, id=member_id),
            input_list[1],
        )
        private_key = input_list[2][2:] if len(input_list) == 3 else "None"

        if (private_key != "None") and (not input_list[2].startswith("0x")):
            return await ctx.send("**Invalid Private key.**\nIt must start with `0x`")

        if not ronin_address.startswith("ronin:"):
            return await ctx.send(
                "**Invalid ronin address.**\nMake sure it starts with `ronin:`"
            )

        # ? sending the user check embed
        user_check_embed = Embed(
            title="Is This Info Correct?",
            description=f"**user:** {member.mention}\n**ronin address:** `{ronin_address}`\n**private key:** `{private_key}`",
            colour=0xFCED16,
            timestamp=datetime.utcnow(),
        )
        user_check_embed.set_thumbnail(url=member.avatar_url)
        check_msg: Message = await ctx.send(embed=user_check_embed)

        # ? yes or no reactions to see if every thing's right
        for emoji in ("✅", "❌"):
            await check_msg.add_reaction(emoji)

        def check(reaction: Reaction, member: Optional[User] = None):
            return str(reaction.emoji) in ("✅", "❌")

        while True:
            try:
                reaction = await self.bot.wait_for(
                    "raw_reaction_add",
                    timeout=100.0,
                    check=check,
                )
                if reaction.user_id == self.bot.user.id:
                    continue

                if str(reaction.emoji) == "❌":
                    await ctx.send("**Please make sure The data is correct.**")
                    break
                elif str(reaction.emoji) == "✅":
                    if (
                        connect_user_db(
                            discord_id=member.id,
                            ronin_address=ronin_address,
                            private_key=private_key,
                            engine=self.engine,
                        )
                        is None
                    ):
                        await ctx.send("**User is already in db**.")
                        break

                    # ?adding to db
                    else:
                        user_connected_embed = Embed(
                            title="User Connected!",
                            description=f"**User:** {member.mention}\n**Address:** `{ronin_address}`",
                        )
                        user_connected_embed.set_thumbnail(url=member.avatar_url)
                        await ctx.send(embed=user_connected_embed)  # ? to admins
                        await member.send(embed=user_connected_embed)  # ? to user
                        break
            except TimeoutError:
                await ctx.send("**Timed Out.**")
                break
            except Exception:
                break
                raise  #!DEBUG

    @has_role(infinity_team_bot.manager_role_name)
    @command(
        name="disconnect",
        brief="disconnects a user from the scholars database\n```diconnect member(mention/id)```",
    )
    async def disconnect_user(self, ctx: Context, *, input_text: Optional[str]):
        if (not input_text) or (len(input_text) == 0):
            return await ctx.send(
                f"**You haven't provided a member.**\nUse `{self.bot.PREFIX}disconnect member(mention or id)`, make sure it's a user mention not a role mention."
            )
        input_list = input_text.split()

        try:
            member_id = int(input_list[0])
        except Exception:
            try:
                member_id = int(input_list[0][3:-1])
            except Exception:
                return await ctx.send("**Invalid User.**")
        member = get(self.guild.members, id=member_id)

        # ? remove user from db
        if not disconnect_user_db(discord_id=member.id, engine=self.engine):
            return await ctx.send("**User is not in db.**")
        else:
            await ctx.message.add_reaction("🟩")

            disconnect_embed = Embed(
                title="Member Disconnected",
                description=member.mention,
                colour=0xFCED16,
                timestamp=datetime.utcnow(),
            )
            disconnect_embed.set_thumbnail(url=member.avatar_url)
            await ctx.send(embed=disconnect_embed)

    @has_role(infinity_team_bot.manager_role_name)
    @command(
        name="warn",
        brief="warns a user\n```warn member(mention/id) reason(required)```",
    )
    async def warn_user(self, ctx: Context, *, input_text: Optional[str]):
        if (not input_text) or (len(input_text) == 0):
            return await ctx.send(
                f"**You haven't provided a member.**\nUse `{self.bot.PREFIX}warn member reason`, make sure it's a user mention not a role mention."
            )
        input_list = input_text.split()

        try:
            member_id = int(input_list[0])
        except Exception:
            try:
                member_id = int(input_list[0][3:-1])
            except Exception:
                return await ctx.send("**Invalid User.**")

        if len(input_list) == 1:
            return await ctx.send("**You haven't provided a Reason for the Warning.**")

        member, reason = (
            get(self.guild.members, id=member_id),
            " ".join(input_list[1:]),
        )

        if add_warn_db(discord_id=member.id, reason=reason, engine=self.engine) is None:
            return await ctx.send("**User doesn't exist in the database.**")

        else:
            await ctx.message.add_reaction("🟩")

            warn_embed = Embed(
                title="Member Warned",
                colour=0xFCED16,
                timestamp=datetime.utcnow(),
            )
            warn_embed.set_author(
                name=f"by: {str(ctx.author)}", icon_url=ctx.author.avatar_url
            )
            warn_embed.set_thumbnail(url=member.avatar_url)
            warn_embed.add_field(
                name=f"{str(member)}",
                value=f"**Reason:** ```{reason}```",
                inline=True,
            )

            await ctx.send(embed=warn_embed)

            # ? DM MEMBER
            try:
                await member.send(f"**You have been warned for:**\n```{reason}```")
            except Exception:
                pass


def setup(bot):
    bot.add_cog(ManageScholars(bot))
