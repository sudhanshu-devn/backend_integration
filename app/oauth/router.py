from fastapi import APIRouter, Request
from app.config import settings
from app.oauth.fb_token_service import finalize_oauth
from app.schemas import OAuthURLResponse, FacebookUser
from app.storage import save_user

router = APIRouter(prefix="/oauth", tags=["OAuth"])


@router.get("/login", response_model=OAuthURLResponse)
async def generate_oauth_url():
    url = (
        f"https://www.facebook.com/{settings.FB_API_VERSION}/dialog/oauth?"
        f"client_id={settings.FB_APP_ID}&"
        f"redirect_uri={settings.FB_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=public_profile,email,ads_management,business_management"
    )

    return OAuthURLResponse(oauth_url=url)


@router.get("/callback", response_model=FacebookUser)
async def oauth_callback(code: str):
    data = await finalize_oauth(code)

    save_user(data["user_id"], data)

    return FacebookUser(**data)
