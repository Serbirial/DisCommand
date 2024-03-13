import asyncio

import inspect
import re

from collections.abc import Callable

from textwrap import TextWrapper
from functools import wraps, partial
from typing_extensions import (
	Self,
	Any
)


from ..exceptions import CommandCheckError

def _shorten(
	input: str,
	*,
	_wrapper: TextWrapper = TextWrapper(width=100, max_lines=1, replace_whitespace=True, placeholder='…'), #TODO: figure out what placeholder really does
) -> str:
	try:
		# split on the first double newline since arguments may appear after that
		input, _ = re.split(r'\n\s*\n', input, maxsplit=1)
	except ValueError:
		pass
	return _wrapper.fill(' '.join(input.strip().split()))

def _do_checks(checks: list[Callable], context) -> bool:
	"""Does all checks and returns True if they all pass, or False if one doesnt pass.

	Args:
		checks (list[Callable]): The list of checks to execute.
		context: The context to run the check within.

	Raises:
		TypeError: One of the checks are not of type Callable
		CommandCheckError: One of the checks failed.

	Returns:
		bool: True if all the checks pass. False if one doesnt pass.
	"""    
	_checks = []
	for check in checks:
		if not callable(check):
			raise TypeError("Check is not callable.")
		if not check(context) == True:
			pass
		_checks.append(1)
	if len(_checks) != len(checks):
		return False
	else:
		return True


def _command_decorator(decorator) -> Callable:
	"""Allows for a decorator to have un-named and named arguments.

	Args:
		decorator (Callable): The decorator to wrap.

	Returns:
		Callable: The wrapped decorator
	"""
	def layer1(*args, **kwargs):
		def layer2(command):
			return decorator(command, *args, **kwargs)
		return layer2
	return layer1

def _group_command_decorator(decorator) -> Callable:
	"""Copy of `_command_decorator` allowing for usage inside of a class.

	Args:
		decorator (Callable): The decorator to wrap.

	Returns:
		Callable: The wrapped decorator
	"""
	def layer1(*args, **kwargs):
		@wraps(decorator)
		def layer2(command):
			return decorator(command, *args, **kwargs)
		return layer2
	return layer1


class Command:
	"""An instance of a Command, containing all information about the command and a function to invoke it.
	"""    
	def __new__(    cls,
					name: str,
					description: str,
					endpoint: str,
					callback: Callable,
					nsfw: bool = False,
					checks: list[Callable] = [],
					parent: Self = None,
					aliases: list = [],
					**extras
				) -> None:
		new_cls = super().__new__(cls) # NOTE: why do i use __new__ here and __init__ with the command group? oh well

		# Command info
		new_cls.name = name
		new_cls.aliases = aliases
		new_cls.nsfw = nsfw
		new_cls.description = description
		new_cls.parent = parent

		# Actual command data
		new_cls.endpoint = endpoint
		new_cls.callback = callback
		new_cls.checks = checks

		# Setting any extra data
		for key, value in extras.items():
			setattr(new_cls, key, value)


		return new_cls

	async def invoke(self, bot, context): # FIXME: type check context
		"""Invokes the command within the given context, also supplying the command with a reference of `bot`.

		Args:
			bot: Initialized discord.py bot instance.
			context: Context for the command to be ran within.
		"""  
		if _do_checks(self.checks, context) != True:
			raise CommandCheckError("One of the commands checks failed.")

		injected = hooked_wrapped_callback(self, bot, context, self.callback)
		try:
			await injected(**context.args)
		except TypeError:
			await injected()

	def add_check(self, check: Callable) -> None:
		"""Adds a check to the checks list.

		Args:
			check (Callable): The function added to the list.
		"""        
		self.checks.append(check)
		
def hooked_wrapped_callback(command: Command, bot, context, coro: Callable) -> Callable:
	@wraps(coro)
	async def wrapped(**args):
		try:
			ret = await coro(command, bot, context, **args)
		except asyncio.CancelledError:
			return
		except Exception as exc:
			return bot.dispatch("command_error", *(context, exc))
		return ret

	return wrapped

# FIXME: add checks to command group, currently only works with regular command
class CommandGroup:
	"""Represents a group of commands, with a function to invoke the main command, and a list containing all the sub-commands.
	"""    
	def __init__(self, name: str, description: str, endpoint: str, callback: Callable[..., Any], nsfw: bool = False, checks: list[Callable[..., Any]] = [], aliases: list = [], **extras) -> None:
		self.name = name
		self.aliases = aliases
		self.description = description
		self.endpoint = endpoint
		self.nsfw = nsfw

		self.checks = checks
		self.callback =  callback

		self.commands: dict[str, Command] = {}

		# Setting any extra data
		for key, value in extras.items():
			setattr(self, key, value)

	@_group_command_decorator
	def command(func, api_endpoint: str = None, **kwargs) -> Command:
		"""Decorator for turning a regular function into a Command within a Group.

		Args:
			name (str): Name of the command being registered.
			description (str, optional): Description of the command. Defaults to None.
			api_url (str, optional): The commands API endpoint. Defaults to None.
			nsfw (bool, optional): Controls if the command is marked as NSFW-only or not. Defaults to False.

		Returns:
			Command: Command object with all needed data.
		"""

		if not inspect.iscoroutinefunction(func):
			raise TypeError('command function must be a coroutine function')

		aliases = kwargs.pop("aliases", [])
		name = kwargs.pop("name", None)
		description = kwargs.pop("description", None)
		nsfw = kwargs.pop("nsfw", False)

		if not name:
			name = func.__name__

		if not description:
			if func.__doc__ is None:
				desc = 'Help has not been made for this command yet.'
			else:
				desc = _shorten(func.__doc__)
		else:
			desc = description

		_command = Command(
			name=name if name else func.__name__,
			description=desc,
			aliases=aliases,
			callback=func,
			nsfw=nsfw,
			endpoint=api_endpoint,
			parent=group,
			**kwargs
		)
		group.add_command(_command)
		return _command

	async def invoke(self, bot, context):
		"""Invokes the command within the given context, also supplying the command with a reference of `bot`.

		Args:
			bot: Initialized discord.py bot instance.
			context: Context for the command to be ran within.
		"""
		if _do_checks(self.checks, context) != True:
			raise CommandCheckError("One of the commands checks failed.")
		injected = hooked_wrapped_callback(self, bot, context, self.callback)
		try:
			await injected(**context.args)
		except TypeError:
			await injected()

	def add_command(self, command: Command) -> None:
		"""Adds a command to the list of sub-commands, this should not be invoked manually unless you know what you are doing.

		Args:
			command (Command): The command to be added to the list.

		Raises:
			TypeError: Returned if the given command is not a subclass of Command.
		"""        
		if not isinstance(command, Command):
			raise TypeError('The command passed must be a subclass of Command')
		
		command.parent = self
		self.commands[command.name] = command

	def add_check(self, check: Callable) -> None:
		"""Adds a check to the checks list.

		Args:
			check (Callable): The function added to the list.
		"""        
		self.checks.append(check)


@_command_decorator
def command(func, api_endpoint: str = None, **kwargs) -> Command:
	"""Decorator for turning a regular function into a Command.

	Args:
		name (str): Name of the command being registered.
		description (str, optional): Description of the command. Defaults to None.
		api_url (str, optional): The commands API endpoint. Defaults to None.
		nsfw (bool, optional): Controls if the command is marked as NSFW-only or not. Defaults to False.

	Returns:
		Command: Command object with all needed data.
	"""
	if not inspect.iscoroutinefunction(func):
		raise TypeError('command function must be a coroutine function')

	aliases = kwargs.pop("aliases", [])
	name = kwargs.pop("name", None)
	description = kwargs.pop("description", None)
	nsfw = kwargs.pop("nsfw", False)

	if not name:
		name = func.__name__

	if not description:
		if func.__doc__ is None:
			desc = 'Help has not been made for this command yet.'
		else:
			desc = _shorten(func.__doc__)
	else:
		desc = description

	_command = Command(
		name=name if name else func.__name__,
		aliases=aliases,
		description=desc,
		callback=func,
		nsfw=nsfw,
		endpoint=api_endpoint,
		**kwargs # Add any extras
	)
	return _command

@_command_decorator
def group(func, api_endpoint: str = None, **kwargs) -> Command:
	"""Decorator for turning a regular function into a Group Command.

	Args:
		name (str): Name of the command being registered.
		description (str, optional): Description of the command. Defaults to None.
		api_url (str, optional): The commands API endpoint. Defaults to None.
		nsfw (bool, optional): Controls if the command is marked as NSFW-only or not. Defaults to False.

	Returns:
		Command: Command object with all needed data.
	"""
	if not inspect.iscoroutinefunction(func):
		raise TypeError('command function must be a coroutine function')

	aliases = kwargs.pop("aliases", [])
	name = kwargs.pop("name", None)
	description = kwargs.pop("description", None)
	nsfw = kwargs.pop("nsfw", False)

	if not name:
		name = func.__name__

	if not description:
		if func.__doc__ is None:
			desc = 'Help has not been made for this command yet.'
		else:
			desc = _shorten(func.__doc__)
	else:
		desc = description

	_command = CommandGroup(
		name=name if name else func.__name__,
		aliases=aliases,
		description=desc,
		callback=func,
		nsfw=nsfw,
		endpoint=api_endpoint,
		**kwargs # Add any extras
	)
	return _command


@_command_decorator
def check(command: Command, func: Callable) -> Command:
	"""Decorator for adding a check to the command.
	"""
	if not callable(func):
		raise CommandCheckError("Check function is not callable")
	if not type(command) in [Command, CommandGroup]:
		raise TypeError("Command does not subclass Command class.")
	
	command.add_check(func)

	return command