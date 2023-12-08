import asyncio

from . import task
from collections.abc import Callable

from functools import wraps

def hooked_wrapped_callback(bot, coro: Callable) -> Callable:
	@wraps(coro)
	async def wrapped(args):
		try:
			ret = await coro(bot, *args)
		except asyncio.CancelledError:
			return
		except TypeError:
			ret = await coro(bot, args)
		except Exception as exc:
			raise exc
		return ret

	return wrapped

class EventManager:
	def __init__(self, bot):
		self.client = bot
		self.listeners = bot.cog_manager.events
        

	def dispatcher(self, event: str, /, *args, **kwargs):
		method = f"on_{event}" 

		if method in self.listeners:
			for event in self.listeners[method]:
				injected = hooked_wrapped_callback(self.client, event.callback)
				task.run_in_background(injected(args))