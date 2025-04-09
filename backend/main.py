from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from backend.Ldap import LDAP
from backend.Routes import Routes
from backend.Htpasswd import Htpasswd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

HTPASSWD_FILE = os.path.join(DATA_DIR, ".htpasswd")

ldap = LDAP()
htpasswd = Htpasswd(HTPASSWD_FILE)

# if __name__ == "__main__":
Routes(app, ldap, htpasswd, BASE_DIR)
