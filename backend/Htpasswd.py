import os, secrets

class	Htpasswd:
	def __init__(self, filepath):
		self.filepath = filepath
		if not os.path.exists(self.filepath):
			open(self.filepath, 'a').close()

	def	get_filepath(self):
		return self.filepath

	def read(self):
		with open(self.filepath, 'r') as f:
			users = [line.strip().split(':', 1) for line in f.readlines()]
		return [{"username": u[0], "password": u[1]} for u in users if len(u) == 2]

	def add(self, username):
		password = secrets.token_hex(8)
		users = self.read()
		if any(user["username"] == username for user in users):
			raise ValueError(f"{username} already exists")
		with open(self.filepath, "a") as f:
			f.write(f"{username}:{password}\n")
		return password

	def delete(self, username):
		users = self.read()
		with open(self.filepath, "w") as f:
			for user in users:
				if user["username"] != username:
					f.write(f"{user['username']}:{user['password']}\n")
