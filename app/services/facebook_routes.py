from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.facebook.client import fb_get
from app.services.facebook.campaigns import create_campaign
from app.services.facebook.adsets import create_adset
from app.services.facebook.ads import create_ad

router = APIRouter(prefix="/facebook", tags=["Facebook Ads"])


### Request Models -----------------------------
class CampaignInput(BaseModel):
    account_id: str
    name: str
    objective: str
    access_token: str

class AdSetInput(BaseModel):
    account_id: str
    campaign_id: str
    name: str
    daily_budget: int
    start_time: str
    end_time: str
    access_token: str
    targeting: Optional[Dict[str, Any]] = None  

class AdInput(BaseModel):
    account_id: str
    adset_id: str
    page_id: str
    ad_name: str
    image_hash: str
    message: str
    link: str
    access_token: str


### ROUTES -------------------------------------

@router.get("/ad_accounts")
async def get_ad_accounts(access_token: str):
    return await fb_get("me/adaccounts", {"access_token": access_token})



@router.post("/campaigns/create")

@router.post("/campaigns/create")
async def api_create_campaign(
    account_id: str,
    name: str,
    objective: str = "OUTCOME_ENGAGEMENT",
    access_token: str = ""
):
    
    # Await the async create_campaign function
    return await create_campaign(account_id, name, objective, access_token, special_ad_categories=["NONE"])


class CampaignGetInput(BaseModel):
    campaign_id: str
    access_token: str


@router.get("/campaigns/get")
async def api_get_campaign(campaign_id: str, access_token: str):
    """
    Get campaign details by campaign ID
    """
    import httpx

    FB_API_URL = "https://graph.facebook.com/v22.0"
    url = f"{FB_API_URL}/{campaign_id}"

    params = {
        "fields": "id,name,objective,status,effective_status,created_time",
        "access_token": access_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"]["message"])

    return data


@router.post("/adsets/create")
async def api_create_adset(data: AdSetInput):
    # If no targeting provided, use a default broad audience
    targeting = data.targeting or {
        "geo_locations": {"countries": ["US"]},  # Minimum required
        "age_min": 18,
        "age_max": 65,
        "genders": [1, 2]
    }

    return await create_adset(
        account_id=data.account_id,
        campaign_id=data.campaign_id,
        name=data.name,
        daily_budget=data.daily_budget,
        start_time=data.start_time,
        end_time=data.end_time,
        access_token=data.access_token,
        targeting=targeting  # Pass targeting to service
    )



@router.post("/ads/create")
async def api_create_ad(data: AdInput):
    return await create_ad(**data.dict())