import sys
import importlib.util
import importlib.machinery

from typing_extensions import (
    Self,
    Any
)

from ..exceptions import (
    CogNotFoundFromSpec,
    FailedLoadingCog,
    CogExportsNotFound,
    CogExportsBad
)

from .commands import (
    Command,
    CommandGroup
)

from .events import Event

class Cog(object):
    """Represents a collection of commands.
    """    
    def __new__(cls, name: str, **kwargs: Any) -> Self:
        self = super().__new__(cls)
        name = name
        
        commands = {}
        events = {}
        # Get all methods that are of the Command type
        command_list = [getattr(self, attribute) for attribute in dir(self) if type(getattr(self, attribute)) in [Command, CommandGroup]]
        event_list = [getattr(self, attribute) for attribute in dir(self) if type(getattr(self, attribute)) == Event]
        for method in command_list:
            commands[method.name] = method
        for method in event_list:
            events[method.name] = method

        new_cls = super().__new__(cls)
        new_cls.name = name
        new_cls.commands = commands
        new_cls.events = events
        new_cls.kwargs = kwargs

        return new_cls


def abort(name, error: CogNotFoundFromSpec | FailedLoadingCog | CogExportsNotFound):
    del sys.modules[name]
    raise error


async def _load_cog_from_spec(bot, spec: importlib.machinery.ModuleSpec, name: str) -> None:
    lib = importlib.util.module_from_spec(spec)
    sys.modules[name] = lib

    # Actually load file.
    try:
        spec.loader.exec_module(lib)  # type: ignore
    except Exception as e:
        abort(name, FailedLoadingCog(f"Cog errored while loading:\n{e}"))

    if not getattr(lib, 'export'):
        abort(name, CogExportsNotFound(f"Export function not found within '{name}'."))

    exports = lib.export(bot)

    def check_exports(_exports):
        if not "cog" in _exports or "name" not in _exports:
            return False
        else:
            return True
    if not check_exports(exports):
        abort(name, CogExportsBad)

    return exports