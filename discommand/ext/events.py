import inspect

from discord import (
    Message,
    Client,
    AutoShardedClient
) 
from typing import (
    Any,
    Callable,
    Coroutine
)
from .commands import (
    Command,
    CommandGroup
)

from .context import Context

def _create_context(
        message: Message,
        bot: Client | AutoShardedClient,
        args: list[Any],
        prefix: str | Callable | Coroutine,
        command: Command | CommandGroup,
        invoked_with: Command | CommandGroup,
        kwargs: dict[str, Any] = {},
        invoked_parent: CommandGroup = None,
        invoked_subcommand: Command = None,
        cls: Context = None): # FIXME: typing
    _cls = cls or Context

    return _cls(
        message=message,
        bot=bot,
        args=args,
        kwargs=kwargs,
        prefix=prefix,
        command=command,
        invoked_with=invoked_with,
        invoked_parent=invoked_parent,
        invoked_subcommand=invoked_subcommand
    )

def _has_prefix(prefixes: list, message: Message) -> str:
    for prefix in prefixes:
        if len(message.content.split(prefix))==2:
            return prefix

def _find_command(bot: Client | AutoShardedClient, prefix: str, content: str) -> Command | None: 
    name = content.split(prefix, 1)[1].split(" ")
    if len(name)>=2:
        if name[1] in bot.sub_commands:
            return bot.sub_commands[name[1]]
    return bot.all_commands[name[0]] if name[0] in bot.all_commands else None
    
def _process_arguments(content: str):
    pass
    
def _find_args(command: Command, message: Message) -> dict[str, str]:
    #args = inspect.getargspec(command.callback)[0]
    return message.content.split(command.name, 1)[1].strip().split(" ")
    
def process_message(bot: Client | AutoShardedClient, prefixes: str | list, message: Message, context = None) -> Command:
    """Processes a message, for retrieving a command if the message contains the prefix+command combination.

    Args:
        bot (Client | AutoShardedClient): Initialized discord.py bot.
        prefixes (str | list): either a string or a list of prefixes.
        message (Message): The message processed for a command.

    Returns:
        Command: The command found
        Args (dict): All found args
    """
    if (prefix := _has_prefix(prefixes, message)):
        print(f"prefix found: {prefix}")
        if (command := _find_command(bot, prefix, message.content)):
            if type(command) == CommandGroup:
                print("Found Command Group")
            args = _find_args(command, message)
            print(command.name)
            print(args)

            context = _create_context(message, bot, args=args, kwargs={}, prefix=prefixes, command=command, invoked_with=command, cls=context)
            print(context)
            return command, args, context