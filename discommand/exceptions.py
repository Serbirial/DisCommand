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
<<<<<<< Updated upstream
=======
    pass

class NoSubCommands(FailedLoadingCog):
    pass

class Invalidevent(Exception):
>>>>>>> Stashed changes
    pass