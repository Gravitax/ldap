from pydantic import BaseModel

class	LoginData(BaseModel):
	username	: str
	password	: str

class	User(BaseModel):
	token		: str
	username	: str
