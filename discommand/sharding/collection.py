import multiprocessing 

from .shard import Shard

class ThreadedCluster:
	def __init__(self, name: str, id: int, client = None) -> None:
		self.id = id
		self.client = client

		self.processes = {}

		self.threads = {}

	def set_client(self, client):
		self.client = client


	def add_thread(self, ids: list[int] | int):
		if not self.client:
			raise Exception("Cannot add thread shard without adding client first.")
		print(ids)
		shard = Shard(len(self.threads.keys())+1, ids, self.client)
		self.threads[shard.id] = shard

	def launch(self, token: str, shard_count: int, *client_args):
		print(self.threads)
		print("Initializing and logging in shards...")
		for sid, shd in self.threads.items():
			print(f"Shard {sid} ({shd.shard_range}) initializing...")
			shd.init_shard(shard_count, *client_args if client_args else ())
			process = multiprocessing.Process(target=shd.login, args=(token, ))
			self.processes[sid] = process

		print("All Shards ready to start.\n\nStarting now...\n")

		for proc in self.processes.values():
			proc.start()

		for _proc in self.processes.values():
			_proc.join()
