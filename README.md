# discommand
 Discord.py Custom command logic, from the ground up.


## Example usage

```py

# Loading a cog and invoking commands.

from discommand.entry import inject

from discord.ext.commands import AutoShardedBot


class YourBot(AutoShardedBot):
		super().__init__(
			command_prefix="!",
			case_insensitive=True)

	async def on_message(self, message: discord.Message):
		"""Message handler to process commands.

		Args:
			message (discord.Message): The message to process.
		"""
		if message.author.bot:
			return
		_context = await self.get_context(message)
		if not _context.command is None:
			return await _context.command.invoke(self, _context)

	async def on_ready(self):
        print("Loading all cogs in 'cogs/'")
        await self.cog_manager.start_load_cogs("cogs/")
        # You need a folder called 'cogs' and within it, the code at the end of this codeblock

def main():
	bot = YourBot()
	inject.inject_into_bot(bot)
	lana.run("YOUR TOKEN HERE")

# COG CODE

from dis_command.ext import commands
from dis_command.ext import cogs


def is_not_bot(context):
    return context.author.bot == False


class TestCog(cogs.Cog):
    """ Various commands that control the configuration of the bot and its workings."""

    def __init__(self, bot) -> None:
        self.client = bot
        # NOTE: COMMANDS CANNOT ACCESS ANYTHING INSIDE OF THE COG. 
        # I WILL BE ADDING A DECORATOR THAT PASSES DATA TO THE COMMAND, AS COMMANDS ARE ENTIRELY DIFFERENT LOGIC WISE.
        # THIS IS BOTH A SECURITY FEATURE, AND AN ISSUE WITH THE CUSTOM COMMAND LOGIC.
    
    @commands.check(is_not_bot)
    @commands.command("reply")
    async def reply(self, bot, ctx):
        ''' Custom command logic test. '''
        return await ctx.send(f"Endpoint: {self.endpoint}\nName: {bot.user}")

    @commands.group("test")
    async def test(self, bot, ctx):
        ''' Custom command logic test. '''
        return await ctx.send(f"Endpoint: {self.endpoint}")
    
    @test.command("test2")
    async def test2(self, bot, ctx):
        ''' Custom command logic test. '''
        return await ctx.send(f"Endpoint: {self.endpoint} (parents: {ctx.command.parent.endpoint})")

def export(bot):
    return {
        "cog": TestCog(bot),
        "name": "Testing Cog"
    }


```