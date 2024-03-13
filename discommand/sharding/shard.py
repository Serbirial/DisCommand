from discord import AutoShardedClient
from threading import Thread

class Shard:
	def __init__(self, id: int, shard_range: list[int, int], client: AutoShardedClient) -> None:
		self.id = id

		self.shard_range = shard_range
		self.client = client

	def init_shard(self, shard_count):
		self.client.shard_count = shard_count 
		self.client.shard_ids = self.shard_range

	def login(self, token):
		self.client.run(token)
