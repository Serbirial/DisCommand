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
        invoked_subcommand=invoked_subcommand,
        view=None
    )

def _has_prefix(prefixes: list, message: Message) -> str:
    for prefix in prefixes:
        try:
            if len(message.content.split(prefix))==2:
                return prefix
        except ValueError:
            pass

def _find_command(bot: Client | AutoShardedClient, prefix: str, content: str) -> Command | None: 
    name = content.split(prefix, 1)[1].split(" ")
    if len(name)>=2:
        try:
            if bot.all_commands[name[0]] == bot.sub_commands[name[1]].parent:
                return bot.sub_commands[name[1]]
            elif name[0] in bot.all_commands:
                return bot.all_commands[name[0]]
        except KeyError:
            if name[0] in bot.all_commands:
                return bot.all_commands[name[0]]
    else:
        return bot.all_commands[name[0]] if name[0] in bot.all_commands else None
    
def _process_arguments(content: str):
    pass
    
def _find_args(command: Command, message: Message) -> dict[str, str]:
    try:
        args = inspect.getfullargspec(command.callback)[0]
    except ValueError:
        args = inspect.signature(command.callback)
    
    given_args = {}
    if not len(args)>3:
        return None
    del args[:3]
    iteration = 0
    _temp = ""
    for arg in message.content.split(command.name, 1)[1].strip().split(" "):
        if iteration>=len(args):
            _temp += arg
        else: 
            given_args[args[iteration]] = arg
            iteration += 1
    given_args[args[-1]] += _temp

    return given_args
    
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
    if (prefix := _has_prefix(prefixes, message)) and (command := _find_command(bot, prefix, message.content)):
        args = _find_args(command, message)

        print(f"Args: {args}")
        context = _create_context(message, bot, args=args, kwargs={}, prefix=prefixes, command=command, invoked_with=prefix, cls=context)
        return command, context
    print(command)
    return None, message.channel