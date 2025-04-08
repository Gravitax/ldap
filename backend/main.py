from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import secrets

from backend.Ldap import LDAP
from backend.type import LoginData, User

app = FastAPI()
myLDAP = LDAP()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

HTPASSWD_FILE = os.path.join(DATA_DIR, ".htpasswd")
	
def			api_response(code, message, token=None):
	return {
		"status"	: code,
		"message"	: message,
		"token"		: token
	}

def         token_generate(token: str):
	return token

def         token_check(token: str):
	return token == "admin"

# ===== LOGIN
@app.post("/login")
def		 login(data: LoginData):
	entries = myLDAP.get_access(data)
	
	if not entries:
		return api_response(404, "User not found")
	user = entries[0]
	stored_password = user.userPassword.value

	if data.password != stored_password:
		return api_response(400, "Invalid password")
	return api_response(200, f"""
		Connexion réussie;<br />
		dn: {user.entry_dn};<br />
		cn: {user.cn.value};<br />
		sn: {user.sn.value};<br />
		givenName: {user.givenName.value};<br />
		mail: {user.mail.value}<br />
	""", token_generate(user.cn.value))

# ========== HTPASSWD

# ===== READ
def		 htpasswd_read():
	if not os.path.exists(HTPASSWD_FILE):
		return []
	with open(HTPASSWD_FILE, "r") as f:
		users = [line.strip().split(":", 1) for line in f.readlines()]
	return [{"username": user[0], "password": user[1]} for user in users if len(user) == 2]

# ===== SEARCH
@app.post("/htpasswd/search")
async def	htpasswd_search(data: LoginData):
	if token_check(data.token) == False:
		raise HTTPException(status_code=400, detail="invalid token")
	users = htpasswd_read()

	for user in users:
		if user["username"] == data.username:
			if user["password"] == data.password:
				return api_response(200, "found")
			else:
				break
	raise HTTPException(status_code=404, detail="not found")

# ===== LIST
@app.get("/htpasswd/list")
async def	htpasswd_list(token: str = Query(...)):
	if token_check(token) == False:
		raise HTTPException(status_code=400, detail="invalid token")
	return htpasswd_read()

# ===== ADD
@app.post("/htpasswd/add")
async def	htpasswd_add(data: User):
	if token_check(data.token) == False:
		raise HTTPException(status_code=400, detail="invalid token")
	password = secrets.token_hex(8)
	users = htpasswd_read()

	if any(user["username"] == data.username for user in users):
		raise HTTPException(status_code=400, detail=f"{data.username} already exist")
	with open(HTPASSWD_FILE, "a") as f:
		f.write(f"{data.username}:{password}\n")
	return api_response(200, f"{data.username} added with password: {password}")

# ===== DELETE
@app.post("/htpasswd/delete")
async def	htpasswd_delete(data: User):
	if token_check(data.token) == False:
		raise HTTPException(status_code=400, detail="invalid token")
	users = htpasswd_read()

	with open(HTPASSWD_FILE, "w") as f:
		for user in users:
			if user["username"] != data.username:
				f.write(f"{user['username']}:{user['password']}\n")
	return api_response(200, f"{data.username} deleted")

# ========== FRONT

@app.get("/")
async def	root():
	return FileResponse(os.path.join(BASE_DIR, "index.html"), media_type="text/html")
