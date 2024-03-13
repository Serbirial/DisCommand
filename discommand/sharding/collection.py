import multiprocessing 

from .shard import Shard

class ThreadedCluster:
	"""A 'Threaded' Cluster of bot instances, each thread carrying on a set ammount of shard IDs.
	"""	
	def __init__(self, name: str, id: int, client = None) -> None:
		self.name = name
		self.id = id
		self.client = client

		self.processes = {}

		self.threads = {}

	def set_client(self, client):
		"""Sets the client for use AFTER initializing the ThreadCluster class.

		Args:
			client (discord.AutoShardedClient): The discord AutoShardedClient
		"""		
		self.client = client

	def add_thread(self, ids: list[int] | int):
		"""Add a new thread of shards to the cluster.

		Args:
			ids (list[int] | int): Either a list of shard IDs for the thread to take control of, or a single shard ID.

		Raises:
			Exception: Client has not been set.
		"""		
		if not self.client:
			raise Exception("Cannot add thread shard without adding client first.")
		shard = Shard(len(self.threads.keys())+1, ids, self.client)
		self.threads[shard.id] = shard

	def launch(self, token: str, shard_count: int, *client_args):
		"""Launches the cluster of shards.

		Args:
			token (str): The bots token.
			shard_count (int): The total shard count needed.
		"""		
		for sid, shd in self.threads.items():
			shd.init_shard(shard_count, *client_args if client_args else ())
			process = multiprocessing.Process(target=shd.login, args=(token, ), daemon=True, name=f"cluster_{self.name}_shard_{sid}")
			self.processes[sid] = process

		for proc in self.processes.values():
			proc.start()
