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
		self._app = app
		self._ldap = ldap
		self._htpasswd = htpasswd
		self.base_dir = base_dir
		self._add_routes()

	def _add_routes(self):
		self._r_connection()
		self._r_htpasswd()
		self._r_front()

	def _r_connection(self):
		@self._app.post("/login")
		async def	login(data: LoginData):
			entries = self._ldap.get_access(data)
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

	def _r_htpasswd(self):
		@self._app.post("/htpasswd/search")
		async def	search(data: LoginData):
			if not Token.check(data.token):
				return api_response(400, "invalid token")
			for user in self._htpasswd.read():
				if user["username"] == data.username:
					if user["password"] == data.password:
						return api_response(200, "found")
					break
			return api_response(404, "not found")

		@self._app.get("/htpasswd/list")
		async def	list(token: str = Query(...)):
			if not Token.check(token):
				return api_response(400, "invalid token")
			return api_response(200, data=self._htpasswd.read())

		@self._app.post("/htpasswd/add")
		async def	add(data: User):
			if not Token.check(data.token):
				return api_response(400, "invalid token")
			try:
				password = self._htpasswd.add(data.username)
			except ValueError as e:
				return api_response(400, str(e))
			return api_response(200, f"{data.username} added with password: {password}")

		@self._app.post("/htpasswd/delete")
		async def	delete(data: User):
			if not Token.check(data.token):
				return api_response(400, "invalid token")
			self._htpasswd.delete(data.username)
			return api_response(200, f"{data.username} deleted")

	def _r_front(self):
		@self._app.get("/")
		async def	root():
			return FileResponse(os.path.join(self.base_dir, "index.html"), media_type="text/html")
