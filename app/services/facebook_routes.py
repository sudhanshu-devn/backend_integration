from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any
import tempfile


from app.services.facebook.client import fb_get
from app.services.facebook.campaigns import create_campaign
from app.services.facebook.adsets import create_adset
from app.services.facebook.ads import create_ad
from app.services.facebook.media import upload_media_service

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

class MediaUploadInput(BaseModel):
    account_id: str
    page_id: str  # required for videos
    access_token: str
    media_type: str  # "video" or "image"
    file_path: str   # local path or S3 path


### ROUTES -------------------------------------
@router.get("/pages")
async def get_pages(access_token: str):
    return await fb_get("me/accounts", {"access_token": access_token})


@router.get("/ad_accounts")
async def get_ad_accounts(access_token: str):
    return await fb_get("me/adaccounts", {"access_token": access_token})


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

@router.post("/media/upload")
async def upload_media(
    account_id: str = Form(...),
    page_id: str = Form(...),  # kept for consistency (FB videos use page later)
    access_token: str = Form(...),
    media_type: str = Form(...),  # "image" or "video"
    file: UploadFile = File(...),
):
    # Save uploaded file temporarily
    ext = file.filename.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp:
        temp.write(await file.read())
        temp_path = temp.name

    # Call service
    result = upload_media_service(
        account_id=f"act_{account_id}",
        media_type=media_type,
        access_token=access_token,
        temp_path=temp_path,
    )

    return result

@router.post("/ads/create")
async def api_create_ad(data: AdInput):
    return await create_ad(**data.dict())