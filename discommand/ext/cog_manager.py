import importlib.util

from os import listdir

from . import cogs
from .commands import Command, CommandGroup
from .events import Event
from ..exceptions import CogNotFoundFromSpec, NoSubCommands

class CogManager:
	def __init__(self, bot) -> None:
		self.client = bot
		self.cached_paths = []

		# FIXME: make internal only and have staticmethod to retrieve
		self._cogs: dict[str, cogs.Cog] = {}

		self.help_dict = {
			0: {}, # Normal commands
			1: {}  # Group commands
		}
		self.events:       dict[str, Event] = {}
		self.all_commands: dict[str, Command | CommandGroup] = {}
		self.sub_commands: dict[str, Command] = {}

	def rebuild_data(self, clear: bool = False):
		del [
			self._cogs,
			self.help_dict,
			self.events,
			self.all_commands,
			self.sub_commands
		]

		# FIXME: make internal only and have staticmethod to retrieve
		self._cogs: dict[str, cogs.Cog] = {}

		self.help_dict = {
			0: {}, # Normal commands
			1: {}  # Group commands
		}
		self.events:       dict[str, Event] = {}
		self.all_commands: dict[str, Command | CommandGroup] = {}
		self.sub_commands: dict[str, Command] = {}

		if clear:
			self.client.all_commands = self.all_commands
			self.client.sub_commands = self.sub_commands

	def build_help_dict(self, command: Command | CommandGroup) -> dict:
			if type(command) == CommandGroup:
				built = {}
				for _name, _command in command.commands.items():
					built[_name] = _command.description
				return built
			else:
				return {
					"desc": command.description
				}
				

	def update_all_commands(self) -> None:
		for _, cog in self._cogs.items():
			for name, command in cog.commands.items():
				if type(command) == CommandGroup:
					if len(command.commands) == 0:
						raise NoSubCommands(f"No sub-commands found when loading command group {command.name}")
					if _ not in self.help_dict[1]:
						self.help_dict[1][_] = {}

					self.all_commands[command.name] = command
					print(f"Adding parent command: {command.name}")
					for _name, _command in command.commands.items():
						print(f"Adding subcommand: {_command.name}")
						self.sub_commands[_command.name] = _command

					self.help_dict[1][_][command.name] = self.build_help_dict(command)
				elif type(command.parent) != CommandGroup:
					if _ not in self.help_dict[0]:
						self.help_dict[0][_] = {}
					print(f"Adding command: {command.name}")
					self.all_commands[command.name] = command
					self.help_dict[0][_][command.name] = self.build_help_dict(command)

			for event in cog.events:
				if event.event_name not in self.events:
					self.events[event.event_name] = [event]
				else:
					self.events[event.event_name].append(event)
				
		self.client.all_commands = self.all_commands
		self.client.sub_commands = self.sub_commands
		self.client.help = self.help_dict


	async def load_cog(self, path: str, update_commands: bool = True) -> None:
		"""Loads a single cog file.

		Args:
			path (str): Full Path to the file containg the cog. 

		Raises:
			CogNotFoundFromSpec: Raised of spec was not found while preparing cog.
		"""
		resolved_name = importlib.util.resolve_name(f"{path.split('.py')[0].replace('/', '.')}", None)
		spec = importlib.util.find_spec(resolved_name)
		if not spec:
			raise CogNotFoundFromSpec(f"Spec was None while attempting to load cog file ({resolved_name}).")
		exports = await cogs._load_cog_from_spec(self.client, spec, None)
		self._cogs[exports["name"]] = exports["cog"]
		if update_commands:
			self.update_all_commands()

	async def load_cogs(self, path: str, update_commands: bool = True) -> None:
		"""Starts loading all .py files in the given path.

		Args:
			path (str): Path to folder containing cog files.

		Raises:
			CogNotFoundFromSpec: Raised of spec was not found while preparing cog.
		"""
		if path not in self.cached_paths:
			self.cached_paths.append(path)
		for file in listdir(path):
			if file.endswith(".py"):
				resolved_name = importlib.util.resolve_name(f"{path.replace('/', '.')}{file.split('.py')[0]}", None)
				spec = importlib.util.find_spec(resolved_name)
				if not spec:
					raise CogNotFoundFromSpec(f"Spec was None while attempting to load cog file ({resolved_name}).")
				exports = await cogs._load_cog_from_spec(self.client, spec, None)
				
				self._cogs[exports["name"]] = exports["cog"]
		if update_commands:
			self.update_all_commands()

	async def unload_cogs(self, autoreload: bool = False):
		"""Unloads all loaded cogs, and optionally: automatically loads them back from file once they are unloaded.

		Args:
			autoreload (bool, optional): Flag for automatically reloading everything from the cached paths. Defaults to False.
		"""		
		self.rebuild_data()
		if autoreload:
			for path in self.cached_paths:
				await self.load_cogs(path, update_commands=False)
		self.update_all_commands()

