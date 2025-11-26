from fastapi import APIRouter, Query
from app.services.fb_ad_service import get_user_ad_accounts

router = APIRouter(prefix="/ad_accounts", tags=["ad_accounts"])

@router.get("/")
async def fetch_ad_accounts(access_token: str = Query(..., description="User's Facebook access token")):
    """
    Get Facebook Ad Accounts for a user.
    """
    accounts = get_user_ad_accounts(access_token)
    return accounts