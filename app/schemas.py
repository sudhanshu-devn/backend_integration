from pydantic import BaseModel, EmailStr

class OAuthURLResponse(BaseModel):
    oauth_url: str

class FacebookUser(BaseModel):
    user_id: str
    name: str | None = None
    email: EmailStr | None = None
    access_token: str