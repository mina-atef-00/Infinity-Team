from datetime import datetime
from discord import Member, User, TextChannel, Embed, user
from discord.ext.commands import Cog, command, cooldown, when_mentioned, BucketType
from typing import Optional
from discord.ext.commands.core import Command, guild_only, has_permissions, has_role
from discord.utils import get
from discord.ext.menus import MenuPages, ListPageSource

from SETUP import mystic_titans_bot


# def syntax(command: Command):
#     cmd_and_aliases = "|".join(sorted([str(command) for command in command.aliases]))
#     params = list()

#     for key, value in command.params.items():
#         if key not in ("self", "ctx"):
#             params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

#     params = " ".join(params)

#     return f"""`{command}|{cmd_and_aliases} {params}`"""


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        super().__init__(data, per_page=5)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        help_embed = Embed(
            title="Help",
            description=f"```{self.ctx.bot.PREFIX}command <arguments>```",
            colour=self.ctx.author.colour,
        )
        help_embed.set_thumbnail(url=self.ctx.bot.user.avatar_url)
        help_embed.set_author(name="Hot-Bot-Pol-Pot")
        help_embed.set_footer(
            text=f"{offset:,} - {min(len_data,offset+self.per_page-1):,} of {len_data:,} commands."
        )

        for name, value in fields:
            help_embed.add_field(name=name, value=value, inline=False)
        return help_embed

    async def format_page(self, menu, entries):
        fields = list()
        for entry in entries:
            fields.append((f"{entry}", f"{(entry.brief or 'No description')}"))
        return await self.write_page(menu, fields)


class BotRelated(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.bot.remove_command("help")  # removing the standard 'help' cmd

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("bot_related")
        else:
            print("bot_related cog loaded")

    @guild_only()
    async def cmd_help(
        self, ctx, command
    ):  # func that creates and embed that has cmd in title, syntax of it in description and takes the command  as an arg
        cmd_help_embed = Embed(
            title=f"`{command}`", description=command.brief or "No description"
        )  # syntax of the cmd as defined in cogs

        await ctx.send(embed=cmd_help_embed)  # sending the embed

    @guild_only()
    # @has_role(mystic_titans_bot.manager_role_name)
    @command(
        name="help", brief="shows the commands, their usage and syntax"
    )  # the overridden help cmd
    @guild_only()
    async def show_help(
        self, ctx, cmd: Optional[str]
    ):  # m'help cmd_name, either u enter a command name of its None
        if not cmd:  # printing an embed including all cmds
            menu = MenuPages(
                source=HelpMenu(ctx, list(self.bot.commands)),
                clear_reactions_after=True,
                timeout=180,
            )
            await menu.start(ctx)
        else:
            if command != get(self.bot.commands, name=cmd):
                await self.cmd_help(ctx, command)
            else:
                await ctx.send("Command doesn't exist!")


def setup(bot):
    bot.add_cog(BotRelated(bot))
