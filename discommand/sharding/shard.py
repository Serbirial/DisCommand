from discord import AutoShardedClient
from threading import Thread

class Shard:
	def __init__(self, id: int, shard_range: list[int, int], client: AutoShardedClient) -> None:
		self.id = id

		self.shard_range = shard_range
		self.client = client

		self.login_thread = Thread(target=self.login, args=)


	def init_shard(self, shard_count):
		self.client.shard_count = shard_count 
		self.client.shard_ids = self.shard_range

	def _actual_login(self, token):
		self.client.run(token)

	def login(self, token):
		self.login_thread = Thread(target=self._actual_login, args=(token,))