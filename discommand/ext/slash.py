import inspect

from discord import (
	app_commands,
	Client,
	AutoShardedClient
)
from discord.app_commands import Command as SlashCommand

from collections.abc import Callable
from .commands import Command
from functools import wraps

from typing_extensions import (
	Self,
	Any
)

def _slash_decorator(decorator) -> Callable:
	def layer1(*args, **kwargs):
		@wraps(decorator)
		def layer2(command):
			return decorator(command, *args, **kwargs)
		return layer2
	return layer1

class ConvertedSlashCommand:
	def __init__(self, command: Command) -> None:
		pass


class SlashCommandTree:
	def __init__(self, client: Client | AutoShardedClient) -> Self:
		self.tree: app_commands.CommandTree = app_commands.CommandTree(client)

		self.converted = {}

	@_slash_decorator
	def make_slash_compatible(self, command: Command) -> ConvertedSlashCommand:
		if not type(command) == Command:
			return Exception("Can only make regular commands slash compatible.")


		_slash_command = SlashCommand(
			callback=command.callback,
			name=command.name,
			description=command.description,
			nsfw=command.nsfw,
			extras={0: command},
			parent=None
		)
		self.tree.add_command(command)