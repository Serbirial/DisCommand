import importlib.util

from os import listdir

from . import cogs
from .commands import Command, CommandGroup
from .events import Event
from ..exceptions import CogNotFoundFromSpec, NoSubCommands

class CogManager:
    def __init__(self, bot) -> None:
        self.client = bot

        # FIXME: make internal only and have staticmethod to retrieve
        self._cogs: dict[str, cogs.Cog] = {}

        self.help_dict = {
            0: {}, # Normal commands
            1: {}  # Group commands
        }
        self.events:       dict[str, Event] = {}
        self.all_commands: dict[str, Command | CommandGroup] = {}
        self.sub_commands: dict[str, Command] = {}


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

                    self.all_commands[name] = command
                    print(f"Adding parent command: {name}")
                    for _name, _command in command.commands.items():
                        print(f"Adding subcommand: {_name}")
                        self.sub_commands[_name] = _command

                    self.help_dict[1][_][command.name] = self.build_help_dict(command)
                elif type(command.parent) != CommandGroup:
                    if _ not in self.help_dict[0]:
                        self.help_dict[0][_] = {}
                    print(f"Adding command: {name}")
                    self.all_commands[name] = command
                    self.help_dict[0][_][command.name] = self.build_help_dict(command)
                
            for event in cog.events:
                if event.event_name not in self.events:
                    self.events[event.event_name] = [event]
                else:
                    self.events[event.event_name].append(event)
                
        self.client.all_commands = self.all_commands
        self.client.sub_commands = self.sub_commands
        self.client.help = self.help_dict
        print(self.help_dict)
        print(self.events)

    async def start_load_cogs(self, path: str) -> None:
        """Starts loading all .py files in the given path.

        Args:
            path (str): Path to folder containing cog files.

        Raises:
            CogNotFoundFromSpec: Raised of spec was not found while preparing cog.
        """        
        for file in listdir(path):
            if file.endswith(".py"):
                resolved_name = importlib.util.resolve_name(f"{path.replace('/', '.')}{file.split('.py')[0]}", None)
                spec = importlib.util.find_spec(resolved_name)
                if not spec:
                    raise CogNotFoundFromSpec("Spec was None while attempting to load cog file.")
                exports = await cogs._load_cog_from_spec(self.client, spec, None)
                
                self._cogs[exports["name"]] = exports["cog"]
        self.update_all_commands()