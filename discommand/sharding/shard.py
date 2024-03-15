from discord import AutoShardedClient
from threading import Thread

class Shard:
	def __init__(self, id: int, shard_range: list[int, int], client: AutoShardedClient, **kwargs) -> None:
		self.id = id

		self.raw_client: AutoShardedClient = client
		self.shard_range = shard_range


	def init_shard(self, internal_name, shard_count, *client_args):
		self.client = self.raw_client(internal_name=internal_name, *client_args if client_args else None)
		self.client.shard_ids = self.shard_range
		self.client.shard_count = shard_count 


	def login(self, token):
		self.client.run(token)
