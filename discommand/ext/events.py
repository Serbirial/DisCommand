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

def _event_decorator(decorator) -> Callable: # FIXME: dont have same code in 2 files
	"""Allows for a decorator to have un-named and named arguments.

	Args:
		decorator (Callable): The decorator to wrap.

	Returns:
		Callable: The wrapped decorator
	"""
	def layer1(*args, **kwargs):
		def layer2(event):
			return decorator(event, *args, **kwargs)
		return layer2
	return layer1


class Event:
	def __new__(    cls,
					event_name: str,
					callback: Callable
				):
		new_cls = super().__new__(cls)
		
		new_cls.event_name = event_name
		new_cls.callback = callback
		
		return new_cls
	
	async def invoke(self):
		return self.callback


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

def _has_prefix(prefixes: list, message: Message, sort: bool = False) -> str:
	if sort:
		prefixes.sort(key=len, reverse=True)
	for prefix in prefixes:
		if message.content.startswith(prefix):
			return prefix

def _look_for_alias(bot: Client | AutoShardedClient, command: str):
	for _command in bot.all_commands.values():
		if command not in _command.aliases:
			pass
		else:
			for alias in _command.aliases:
				if alias == command:
					return _command.name, alias
	return None, None

def _look_for_alias_sub(bot: Client | AutoShardedClient, command: str):
	for _command in bot.sub_commands.values():
		if command not in _command.aliases:
			pass
		else:
			for alias in _command.aliases:
				if alias == command:
					return _command.name, alias
	return None, None

def _find_command(bot: Client | AutoShardedClient, prefix: str, content: str) -> tuple[Command, str | None] | None: 
	try:
		name = content.split(prefix, 1)[1].split(" ")
	except IndexError:
		return None
	if len(name) == 0:
		return
	elif "\n" in name[0]: # Stupid case handling for if theres a newline
		_temp = name[0].split("\n")
		name[0] = _temp[0]
		name[1] = _temp[1] + name[1]

	if len(name) == 1: # Regular command with no args.
		real_name, alias = _look_for_alias(bot, name[0])
		if not alias: 
			return (bot.all_commands[name[0]], None) if name[0] in bot.all_commands else None
		elif alias:
			return (bot.all_commands[real_name], alias) if real_name in bot.all_commands else None
		
	elif len(name)>=2: # Possible sub commands, or regular command with args.
		parent_real, parent_alias = _look_for_alias(bot, name[0])
		if not parent_alias: # Was not a sub-command, doesnt have parent, possibly arguments.
			if name[0] in bot.all_commands and name[1] in bot.sub_commands:
				return (bot.all_commands[name[0]].commands[name[1]], None)
			
			if name[0] in bot.all_commands: # Fallback to make sure atleast the parent command gets executed.
				return (bot.all_commands[name[0]], None)
			
		elif parent_alias:
			sub_real, sub_alias = _look_for_alias_sub(bot, name[1])
			if not sub_alias: # Was not a sub-command, arguments were mistaken for possible sub-commands.
				return (bot.all_commands[parent_real], parent_alias) if parent_real in bot.all_commands else None
			elif sub_alias:
				return (bot.all_commands[sub_real].commands[sub_real], sub_alias) if sub_real in bot.all_commands[parent_alias].commands else None


def _find_args(command: Command, message: Message, alias: str = None) -> dict[str, str]:
	try:
		args = inspect.getfullargspec(command.callback)[0]
	except ValueError:
		args = inspect.signature(command.callback)
	split_content = message.content.split(command.name if alias == None else alias, 1)
	if len(split_content) == 1: # Only the command, no args in the message.
		return None
	given_args = {}
	if not len(args)>3:
		return None
	del args[:3]
	iteration = 0
	_temp = ""
	for arg in split_content[1].strip().split(" "):
		if arg == "":
			continue
		if iteration>=len(args):
			_temp += f" {arg}"
		else: 
			given_args[args[iteration]] = arg
			iteration += 1
	if len(given_args)>0:
		given_args[list(given_args.keys())[-1]] += _temp
	return given_args
	
def process_message(bot: Client | AutoShardedClient, prefixes: str | list, message: Message, context = None, sort_prefixes: bool = False) -> Command:
	"""Processes a message, for retrieving a command if the message contains the prefix+command combination.

	Args:
		bot (Client | AutoShardedClient): Initialized discord.py bot.
		prefixes (str | list): either a string or a list of prefixes.
		message (Message): The message processed for a command.

	Returns:
		Command: The command found
		Args (dict): All found args
	"""
	if prefixes:
		prefix = _has_prefix(prefixes, message, sort_prefixes)
		if prefix:
			command_data = _find_command(bot, prefix, message.content)
			if command_data:
				alias = command_data[1]
				args = _find_args(command_data[0], message, alias)
				context = _create_context(message, bot, args=args, kwargs={}, prefix=prefixes, command=command_data[0], invoked_with=prefix, cls=context)
				return command_data[0], context
	return None, message.channel

	
def inject_events(bot: Client | AutoShardedClient, events: list[Callable]) -> None:
	"""Injects events into bot - WARNING: Will overwrite existing events/functions based on name.

	Args:
		bot (Client | AutoShardedClient): Initialized discord.py bot.
		events (list[Callable]): List of callables to inject.
	"""


@_event_decorator
def register(func, event_name: str = None) -> bool:
	"""Decorator for registering a function as an event.

	Args:
		event_name (str): Name of the event being registered to the function.

	Raises:
		TypeError: Function was not a coroutine.

	Returns:
		bool: True if sucessfully registered to the event manager. False if something went wrong.
	"""

	if not inspect.iscoroutinefunction(func):
		raise TypeError('Event function must be a coroutine function')

	if not event_name:
		event_name = func.__name__

	_event = Event(
		event_name=event_name if event_name else func.__name__,
		callback=func,
	)
	return _event