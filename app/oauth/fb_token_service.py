import httpx
from app.config import settings

FB_VERSION = settings.FB_API_VERSION


async def exchange_code_for_token(code: str) -> dict:
    url = f"https://graph.facebook.com/{FB_VERSION}/oauth/access_token"

    params = {
        "client_id": settings.FB_APP_ID,
        "redirect_uri": settings.FB_REDIRECT_URI,
        "client_secret": settings.FB_APP_SECRET,
        "code": code,
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        return r.json()


async def exchange_for_long_lived_token(short_token: str) -> dict:
    url = f"https://graph.facebook.com/{FB_VERSION}/oauth/access_token"

    params = {
        "grant_type": "fb_exchange_token",
        "client_id": settings.FB_APP_ID,
        "client_secret": settings.FB_APP_SECRET,
        "fb_exchange_token": short_token,
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        return r.json()


async def get_facebook_user(access_token: str) -> dict:
    url = f"https://graph.facebook.com/{FB_VERSION}/me"

    params = {
        "access_token": access_token,
        "fields": "id,name,email",
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        return r.json()


async def finalize_oauth(code: str) -> dict:
    # Step 1: Code → Short-lived token
    short = await exchange_code_for_token(code)

    if "access_token" not in short:
        raise Exception(f"Token error: {short}")

    short_token = short["access_token"]

    # Step 2: Short-lived → Long-lived
    long_token_data = await exchange_for_long_lived_token(short_token)
    long_token = long_token_data["access_token"]

    # Step 3: Fetch user info
    user = await get_facebook_user(long_token)

    return {
        "user_id": user.get("id"),
        "name": user.get("name"),
        "email": user.get("email"),
        "access_token": long_token,
    }
