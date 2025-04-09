import os, secrets

class	Htpasswd:
	def	__init__(self, filepath):
		self.filepath = filepath
		self._ensure_file()
		self.file = open(self.filepath, "r+", encoding="utf-8")
		self._users = self._load_users()

	def	_ensure_file(self):
		if not os.path.exists(self.filepath):
			with open(self.filepath, 'a'):
				pass

	def	_load_users(self):
		self.file.seek(0)
		lines = self.file.readlines()
		users = [line.strip().split(":", 1) for line in lines]
		return [{"username": u[0], "password": u[1]} for u in users if len(u) == 2]

	def	read(self):
		return self._users.copy()

	def	add(self, username):
		if any(user["username"] == username for user in self._users):
			raise ValueError(f"{username} already exists")
		password = secrets.token_hex(8)
		self.file.write(f"{username}:{password}\n")
		self.file.flush()
		self._users.append({"username": username, "password": password})
		return password

	def	delete(self, username):
		self._users = [user for user in self._users if user["username"] != username]
		self._rewrite_file()

	def	_rewrite_file(self):
		self.file.seek(0)
		self.file.truncate()
		for user in self._users:
			self.file.write(f"{user['username']}:{user['password']}\n")
		self.file.flush()

	def	close(self):
		if not self.file.closed:
			self.file.close()

	def __del__(self):
		self.close()
