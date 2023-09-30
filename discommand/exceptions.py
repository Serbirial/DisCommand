class CogNotFoundFromSpec(Exception):
    pass

class FailedLoadingCog(Exception):
    pass

class CogExportsNotFound(Exception):
    pass

class CogExportsBad(Exception):
    pass

class CommandInvokeError(Exception):
    pass

class CommandCheckError(CommandInvokeError):
    pass

class NoSubCommands(FailedLoadingCog):
    pass