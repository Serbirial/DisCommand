from ..ext.cog_manager import CogManager

from discord import (
    Client,
    AutoShardedClient
)

def inject_into_bot(bot):
    if not issubclass(bot.__class__, Client) or not issubclass(bot.__class__, AutoShardedClient):
        raise TypeError("Bot is not of type discord.Client or discord.AutoShardedClient (ext.commands.Bot or ext.commands.AutoShardedBot are not supported as they implement commands themselves.)")
    
    cog_manager = CogManager(bot)
    bot.cog_manager = cog_manager