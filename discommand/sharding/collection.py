from .shard import Shard


class ThreadedCluster:
	def __init__(self, name: str, id: int, client = None) -> None:
		self.id = id
		self.client = client

		self.threads = {}

	def set_client(self, client):
		self.client = client


	def add_thread(self, ids: list[int] | int):
		if not self.client:
			raise Exception("Cannot add thread shard without adding client first.")

		shard = Shard(len(self.shards.keys())+1, ids, self.client)
		self.threads[shard.id] = shard

	def launch(self, token: str, shard_count: int):
		print("Initializing shards...")
		for shd in self.threads.values():
			shd.init_shard(shard_count)
		for sid, shd in self.threads.items():
			print(f"Shard {sid} logging in...")
			shd.login(token)
		print("All shards ready.")