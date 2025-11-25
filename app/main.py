from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from .routers import media
from .models import users_db, User
from .schemas import UserLogin, Token
from .auth import hash_password, verify_password, create_access_token

app = FastAPI(title="Facebook Media Upload API")

app.include_router(media.router)

# Temporary: create some users in memory
users_db["john@example.com"] = User(
    email="john@example.com",
    username="john",
    hashed_password=hash_password("password123"),
    fb_page_id="YOUR_PAGE_ID",
    fb_page_access_token="YOUR_PAGE_ACCESS_TOKEN"
).dict()

# Login route
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(400, "Invalid email or password")
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

# Test route
@app.get("/test")
def test():
    return {"message": "Server is running!"}
