# NOTE: Im gonna commit mass fucking warcrimes

from discord import (
	Client,
	AutoShardedClient
)
from .commands import Command

from typing_extensions import Self

SLASH_INTERACTION = 1
USER_INTERACTION = 2
MESSAGE_INTERACTION = 3

def command_to_json(command: Command):
	json = {
		"name": command.name,
		"type": SLASH_INTERACTION,
		"description": command.description,
		"options": [
			# TODO: actually get the commands arguments and list them here; or implement a way of defining them when calling `add_to_tree`
		]
	}
	return json

class SlashCommandTree:
	def __init__(self, client: Client | AutoShardedClient) -> Self:
		self.client = client
		self.tree: {}

	def register_command(self, command: Command) -> None:
		"""Registers a command to the slash command tree.

		Args:
			command (Command): The command to add to the tree.

		Raises:
			Exception: A command with the same name has already been registered to the tree. Or the command was not of the type `discommand.commands.Command`

		Returns:
			None
		"""		
		if not type(command) == Command:
			return Exception("Can only make regular commands slash compatible.")

		if command.name in self.tree:
			raise Exception("Command already in Tree.")

		self.tree[command.name] = command_to_json(command)

	def check_for_slash(self, command_name: str):
		if command_name in self.tree:
			return self.tree[command_name]
		else:
			return False	