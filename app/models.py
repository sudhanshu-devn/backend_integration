from typing import Dict
from pydantic import BaseModel

# In-memory storage for users
users_db: Dict[str, dict] = {}

class User(BaseModel):
    email: str
    username: str
    hashed_password: str
    fb_page_id: str
    fb_page_access_token: str