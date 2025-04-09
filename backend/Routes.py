from fastapi import Query
from fastapi.responses import FileResponse
import os

from backend.Token import Token
from backend.type import LoginData, User

def api_response(code, message=None, token=None, data=None):
	return {
		"status"	: code,
		"message"	: message,
		"token"		: token,
		"data"		: data
	}

class Routes:
	def __init__(self, app, ldap, htpasswd, base_dir):
		self.app = app
		self.ldap = ldap
		self.htpasswd = htpasswd
		self.base_dir = base_dir
		self.add_routes()

	def add_routes(self):
		self.r_connection()
		self.r_htpasswd()
		self.r_front()

	def r_connection(self):
		@self.app.post("/login")
		async def	login(data: LoginData):
			entries = self.ldap.get_access(data)
			if not entries:
				return api_response(404, "User not found")
			user = entries[0]
			if data.password != user.userPassword.value:
				return api_response(400, "Invalid password")
			return api_response(200, f"""
				Connexion réussie;<br />
				dn: {user.entry_dn};<br />
				cn: {user.cn.value};<br />
				sn: {user.sn.value};<br />
				givenName: {user.givenName.value};<br />
				mail: {user.mail.value}<br />
			""", Token.generate(user.cn.value))

	def r_htpasswd(self):
		@self.app.post("/htpasswd/search")
		async def	search(data: LoginData):
			if not Token.check(data.token):
				return api_response(400, "invalid token")
			for user in self.htpasswd.read():
				if user["username"] == data.username:
					if user["password"] == data.password:
						return api_response(200, "found")
					break
			return api_response(404, "not found")

		@self.app.get("/htpasswd/list")
		async def	list(token: str = Query(...)):
			if not Token.check(token):
				return api_response(400, "invalid token")
			return api_response(200, data=self.htpasswd.read())

		@self.app.post("/htpasswd/add")
		async def	add(data: User):
			if not Token.check(data.token):
				return api_response(400, "invalid token")
			try:
				password = self.htpasswd.add(data.username)
			except ValueError as e:
				return api_response(400, str(e))
			return api_response(200, f"{data.username} added with password: {password}")

		@self.app.post("/htpasswd/delete")
		async def	delete(data: User):
			if not Token.check(data.token):
				return api_response(400, "invalid token")
			self.htpasswd.delete(data.username)
			return api_response(200, f"{data.username} deleted")

	def r_front(self):
		@self.app.get("/")
		async def	root():
			return FileResponse(os.path.join(self.base_dir, "index.html"), media_type="text/html")
