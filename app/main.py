from fastapi import FastAPI
from app.oauth.router import router as oauth_router
from app.media.router import router as media_router
from app.routers.ad_accounts import router as ad_accounts_router

app = FastAPI()

app.include_router(oauth_router)
app.include_router(media_router)
app.include_router(ad_accounts_router)


@app.get("/")
def root():
    return {"message": "Facebook OAuth API is running"}
