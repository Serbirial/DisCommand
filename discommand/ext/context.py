from discord import (
    Message,
    Client,
    AutoShardedClient
)
from discord.channel import DMChannel, GroupChannel, PartialMessageable, StageChannel, TextChannel, VoiceChannel
from discord.threads import Thread 
from .commands import (
    Command,
    CommandGroup
)
from typing import (
    Any,
    Callable,
    Coroutine
)
from discord import (
    TextChannel,
    VoiceChannel,
    StageChannel
)

from discord.embeds import Embed
from discord.abc import Messageable

class Context(Messageable):
    def __init__(
            self,
            *,
            message: Message,
            bot: Client | AutoShardedClient,
            args: list[Any] | str,
            kwargs: dict[str, Any],
            prefix: str | Callable | Coroutine,
            command: Command | CommandGroup,
            invoked_with: Command | CommandGroup,
            invoked_parent: CommandGroup,
            invoked_subcommand: Command
        ) -> None:
        self._message = message
        self.bot = bot
        self.args =  args if args else {}
        self.prefix = prefix
        self.command = command
        self.invoked_with = invoked_with
        self.invoked_parent = invoked_parent
        self.invoked_subcommand = invoked_subcommand


    async def invoke(self, command: Command | CommandGroup):
        return await command.invoke(self.bot, self)

    @property
    def message(self):
        return self._message
    
    @property
    def guild(self):
        return self.message.guild
    
    @property
    def channel(self):
        return self.message.channel
    
    @property
    def author(self):
        return self.message.author
    
    @property
    def me(self):
        return self.guild.me if self.guild else self.bot.user
    

    @property
    def permissions(self):
        _type = type(self.channel)
        #if _type == DMChannel:
        #    return None # FIXME: return DM permissions.
        return self.channel.permissions_for(self.author)
        # FIXME: interactions not implemented

    @property
    def bot_permissions(self):
        return self.channel.permissions_for(self.bot)

    @property
    def valid(self) -> bool:
        return self.prefix is not None and self.command is not None
    


    async def send(self, content: str, tts: bool = False, embed: Embed = None, mention_author: bool = False, delete_after: int = None):
        return await self.channel.send(
            content=content,
            tts=tts,
            embed=embed,
            embeds=None, #FIXME: support multiple embeds, files, stickers
            file=None,
            files=None,
            stickers=None,
            delete_after=delete_after,
            nonce=None,             # FIXME: Support none, mentions, reference
            allowed_mentions=None,
            reference=None,
            mention_author=mention_author,
            view=None, # FIXME: support view, embed supression, and silent flag
            suppress_embeds=None,
            silent=False,
        ) 
    
