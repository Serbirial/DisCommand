import asyncio

from . import task
from collections.abc import Callable

from functools import wraps

def hooked_wrapped_callback(bot, coro: Callable) -> Callable:
	@wraps(coro)
	async def wrapped(args):
		if len(args)==1:
			ret = await coro(bot, args[0])
		else:
			try:
				ret = await coro(bot, *args)
			except asyncio.CancelledError:
				return
			except Exception as exc:
				raise exc
		return ret

	return wrapped

class EventManager:
	def __init__(self, bot):
		self.client = bot

	def dispatcher(self, event: str, /, *args, **kwargs):
		method = f"on_{event}" 

		if method in self.client.cog_manager.events:
			for event in self.client.cog_manager.events[method]:
				injected = hooked_wrapped_callback(self.client, event.callback)
				task.run_in_background(injected(args))