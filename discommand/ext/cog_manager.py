import importlib.util

from os import listdir

from . import cogs
from .commands import Command, CommandGroup
from ..exceptions import CogNotFoundFromSpec

class CogManager:
    def __init__(self, bot) -> None:
        self.client = bot

        # FIXME: make internal only and have staticmethod to retrieve
        self._cogs: dict[str, cogs.Cog] = {}

        self.all_commands: dict[str, Command | CommandGroup] = {}
        self.sub_commands: dict[str, Command] = {}


    def update_all_commands(self) -> None:
        for _, cog in self._cogs.items():
            for name, command in cog.commands.items():
                print(f"Updating: {name}")
                if type(command) == CommandGroup: # Add all the groups sub-commands so discord.py recognizes them too.
                    print("Found Group while updating...")
                    for _name, _command in command.commands.items():
                        self.sub_commands[_name] = _command
                self.all_commands[name] = command
                
        self.client.all_commands = self.all_commands
        self.client.sub_commands = self.sub_commands
<<<<<<< Updated upstream
=======
        self.client.help = self.help_dict
        print(self.help_dict)
>>>>>>> Stashed changes

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