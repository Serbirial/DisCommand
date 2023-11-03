import re

from discord import (
    utils,
    Member
)
from discord.abc import (
    GuildChannel
)

from typing import (
    Any
)

from ..exceptions import ConverterError

_ID_REGEX = r"[0-9]+"

async def member(context, to_convert: Any) -> Member:
    """Converts to_convert to discord.Member if possible.

    Args:
        context: Context within this is invoked.
        to_convert (Any): Argument to convert

    Returns:
        Member: The member found.
    """
    if not to_convert:
        raise ConverterError("Nothing to convert.") 
    if (uid := re.search(_ID_REGEX, to_convert)): # Was mentioned or has UID
        member = context.guild.get_member(int(uid[0]))
        if not member:
            raise ConverterError("Unable to find member while converting argument.")
        return member
    else: # Fall back to using their username
        member = context.guild.get_member_named(to_convert)
        if not member:
            raise ConverterError("Unable to find member while converting argument.")
        return member

async def channel(context, to_convert: Any) -> GuildChannel:
    """Converts to_convert to a channel if possible

    Args:
        context (_type_): Context within this is invoked.
        to_convert (Any): Argument to convert

    Raises:
        ConverterError: Failed to convert to_convert to a channel.

    Returns:
        channel: The found channel
    """    
    if not to_convert:
        raise ConverterError("Nothing to convert.") 
    if (uid := re.search(_ID_REGEX, to_convert)): # Was mentioned or has UID
        return context.guild.get_channel(int(uid[0]))
    try:
        channel = utils.get(context.guild.channels, name=to_convert)
        if channel:
            return channel
        raise ConverterError(f"Failed to convert `{to_convert}` into channel.")
    except:
        raise ConverterError(f"Failed to convert `{to_convert}` into channel.")

async def emoji(context, to_convert: Any):
    if not to_convert:
        raise ConverterError("Nothing to convert.")  
    if (eid := re.search(_ID_REGEX, to_convert)): # Contains possible emoji ID
        return context.bot.get_emoji(int(eid[0]))
    else:
        raise ConverterError(f"Failed to convert `{to_convert}` into emoji.")





async def integer(context, to_convert: Any) -> int:
    """Converts to_convert to an integer is possible

    Args:
        context (_type_): Context within this is invoked.
        to_convert (Any): Argument to convert

    Raises:
        ConverterError: Failed to convert to_convert to an integer.

    Returns:
        int: The converted integer
    """    
    if not to_convert:
        raise ConverterError("Nothing to convert.") 
    try:
        return int(to_convert)
    except:
        raise ConverterError(f"Failed to convert `{to_convert}` into integer.")