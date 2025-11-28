from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException
import httpx
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import tempfile
import shutil
import os

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.advideo import AdVideo


from app.services.facebook.client import fb_get
from app.services.facebook.campaigns import create_campaign
from app.services.facebook.adsets import create_adset
from app.services.facebook.ads import create_video_ad
from app.services.facebook.media import upload_media_service

router = APIRouter(prefix="/facebook", tags=["Facebook Ads"])

FB_API_URL = "https://graph.facebook.com/v22.0"

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

@router.get("/adsets/list")
async def list_adsets(account_id: str = Query(...), access_token: str = Query(...)):
    """
    List all Ad Sets for a given ad account.
    account_id should NOT include 'act_' prefix; only the numeric ID.
    """
    url = f"{FB_API_URL}/act_{account_id}/adsets"

    params = {
        "fields": "id,name,campaign_id,status",
        "access_token": access_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"]["message"])

    return data

@router.get("/adsets/verify/{adset_id}")
async def verify_adset_ownership(
    adset_id: str,
    your_account_id: str = Query(...),
    access_token: str = Query(...)
):
    """
    Verify if an adset belongs to a specific ad account.
    """

    url = f"{FB_API_URL}/{adset_id}"
    params = {
        "fields": "id,account_id,name,status,campaign_id",
        "access_token": access_token,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    # Handle API errors
    if "error" in data:
        raise HTTPException(
            status_code=400,
            detail=data["error"]["message"],
        )

    adset_account = data.get("account_id")

    return {
        "adset_id": adset_id,
        "adset_account_id": adset_account,
        "your_account_id": your_account_id,
        "belongs_to_you": (adset_account == f"act_{your_account_id}"),
        "adset_details": data,
    }

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


@router.post("/adcreatives/create/video")
async def create_video_ad_creative_simple(
    account_id: str = Form(...),
    page_id: str = Form(...),
    ad_name: str = Form(...),
    message: str = Form(...),
    link: str = Form(...),
    access_token: str = Form(...),
    video_id: str = Form(...),
    thumbnail_hash: str = Form(...),
):
    try:
        creative_payload = {
            "name": ad_name,
            "object_story_spec": {
                "page_id": page_id,
                "video_data": {
                    "video_id": video_id,
                    "title": ad_name,
                    "message": message,
                    "image_hash": thumbnail_hash,
                    "call_to_action": {"type": "LEARN_MORE", "value": {"link": link}},
                },
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FB_API_URL}/act_{account_id}/adcreatives",
                params={"access_token": access_token},
                json=creative_payload,
            )
            data = response.json()
            if "error" in data:
                raise HTTPException(status_code=400, detail=data["error"]["message"])

        return {"creative_id": data.get("id"), "creative_data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ads/create/videoAds")
async def api_create_video_ad(
    account_id: str = Form(...),
    adset_id: str = Form(...),
    page_id: str = Form(...),
    ad_name: str = Form(...),
    video_id: str = Form(...),
    thumbnail_hash: str = Form(...),
    message: str = Form(...),
    link: str = Form(...),
    access_token: str = Form(...)
):
    result = await create_video_ad(
        account_id=account_id,
        adset_id=adset_id,
        page_id=page_id,
        ad_name=ad_name,
        video_id=video_id,
        thumbnail_hash=thumbnail_hash,
        message=message,
        link=link,
        access_token=access_token
    )
    return result


# --- Helper functions ---

async def upload_image(account_id: str, access_token: str, file_path: str):
    FacebookAdsApi.init(access_token=access_token)
    image = AdImage(parent_id=account_id)
    image[AdImage.Field.filename] = file_path
    image.remote_create()
    return image[AdImage.Field.hash]

async def upload_video(account_id: str, access_token: str, file_path: str):
    FacebookAdsApi.init(access_token=access_token)
    video = AdVideo(parent_id=account_id)
    video[AdVideo.Field.filepath] = file_path
    video.remote_create()
    return video[AdVideo.Field.id]

@router.post("/ads/create/video/v1")
async def create_video_ad_endpoint(
    account_id: str = Form(...),
    adset_id: str = Form(...),
    page_id: str = Form(...),
    ad_name: str = Form(...),
    message: str = Form(...),
    link: str = Form(...),
    access_token: str = Form(...),
    video_file: UploadFile = File(...),
    thumbnail_file: UploadFile = File(...),
):
    try:
        # Ensure account_id is numeric for media upload
        numeric_account_id = account_id.replace("act_", "")

        # Save uploaded files temporarily
        temp_video_path = f"/tmp/{video_file.filename}"
        temp_thumb_path = f"/tmp/{thumbnail_file.filename}"

        with open(temp_video_path, "wb") as f:
            shutil.copyfileobj(video_file.file, f)

        with open(temp_thumb_path, "wb") as f:
            shutil.copyfileobj(thumbnail_file.file, f)

        # Upload media to Facebook
        video_id = await upload_video(numeric_account_id, access_token, temp_video_path)
        thumbnail_hash = await upload_image(numeric_account_id, access_token, temp_thumb_path)

        # Clean up temp files
        os.remove(temp_video_path)
        os.remove(temp_thumb_path)

        # Create the video ad
        url = f"{FB_API_URL}/act_{numeric_account_id}/ads"
        payload = {
            "name": ad_name,
            "adset_id": adset_id,
            "creative": {
                "object_story_spec": {
                    "page_id": page_id,
                    "video_data": {
                        "video_id": video_id,
                        "title": ad_name,
                        "message": message,
                        "image_hash": thumbnail_hash,
                        "call_to_action": {
                            "type": "LEARN_MORE",
                            "value": {"link": link},
                        },
                    },
                }
            },
            "status": "PAUSED",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, params={"access_token": access_token}, json=payload)
            data = response.json()

        if "error" in data:
            raise HTTPException(status_code=400, detail=data["error"]["message"])

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/ads/publish")
async def publish_ad(
    account_id: str = Form(...),
    adset_id: str = Form(...),
    ad_name: str = Form(...),
    creative_id: str = Form(...),
    access_token: str = Form(...),
    tracking_specs: str = Form("[]"),   # JSON string like JS version
    status: str = Form("PAUSED"),
):
    try:
        # Convert tracking_specs JSON string → Python list
        import json
        try:
            tracking_specs_parsed = json.loads(tracking_specs)
        except:
            tracking_specs_parsed = []

        publish_payload = {
            "name": ad_name,
            "adset_id": adset_id,
            "creative": {"creative_id": creative_id},
            "tracking_specs": tracking_specs_parsed,
            "status": status,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FB_API_URL}/act_{account_id}/ads",
                params={
                    "access_token": access_token,
                    "fields": "status,effective_status,issues_info",
                },
                json=publish_payload,
            )

        data = response.json()
        print("FB DEBUG RESPONSE:", data)  # helpful logger

        if "error" in data:
            raise HTTPException(status_code=400, detail=data)

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
