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
    StageChannel,
    Guild,
    User,
    Member,
    Permissions
)
from discord.ui import View

from discord.embeds import Embed
from discord.abc import Messageable

class Context(Messageable):
    def __init__(
            self,
            *,
            message: Message,
            bot: Client | AutoShardedClient,
            view: View = None,
            args: list[Any] | str,
            kwargs: dict[Any],
            prefix: str | Callable | Coroutine,
            command: Command | CommandGroup,
            invoked_with: Command | CommandGroup,
            invoked_parent: CommandGroup,
            invoked_subcommand: Command
        ) -> None:
        self._message = message
        self.bot = bot
        self.args =  args if args else {}
        self.kwargs = kwargs if kwargs else {} 
        self.view = view
        self.prefix = prefix
        self.command = command
        self.invoked_with = invoked_with
        self.invoked_parent = invoked_parent
        self.invoked_subcommand = invoked_subcommand


    async def invoke(self, command: Command | CommandGroup):
        return await command.invoke(self.bot, self)

    @property
    def message(self) -> Message:
        return self._message
    
    @property
    def guild(self) -> Guild:
        return self.message.guild
    
    @property
    def channel(self) -> TextChannel | VoiceChannel | StageChannel:
        return self.message.channel
    
    @property
    def author(self) -> Member | User | Client | AutoShardedClient: 
        return self.message.author
    
    @property
    def me(self) -> Client | AutoShardedClient:
        return self.guild.me if self.guild else self.bot.user
    

    @property
    def permissions(self) -> Permissions:
        _type = type(self.channel)
        #if _type == DMChannel:
        #    return None # FIXME: return DM permissions.
        return self.channel.permissions_for(self.author)
        # FIXME: interactions not implemented

    @property
    def bot_permissions(self) -> Permissions:
        return self.channel.permissions_for(self.bot)

    @property
    def valid(self) -> bool:
        return self.prefix is not None and self.command is not None
    


    async def send(self, content: str = None, view = None, tts: bool = False, nonce: Any = None, file: Any = None, files: Any = None, stickers: Any = None, embeds: list[Embed] = None, embed: Embed = None, allowed_mentions: bool = True, mention_author: bool = False, silent: bool = False, suppress_embeds: bool = False, delete_after: int = None):
        return await self.channel.send(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            stickers=stickers,
            delete_after=delete_after,
            nonce=nonce,       # NOTE: idk what this is
            reference=None,
            mention_author=mention_author,
            view=view,
            silent=silent,
        ) 
    
