from ..ext.cog_manager import CogManager

def inject_into_bot(bot):
    cog_manager = CogManager(bot)
    bot.cog_manager = cog_manager