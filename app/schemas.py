from pydantic import BaseModel, EmailStr, constr

# create a type alias so the call expression is not used directly in the annotation
PasswordStr = constr(max_length=72)

class UserLogin(BaseModel):
    email: EmailStr
    password: PasswordStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"