from fastapi import APIRouter, Form
from pydantic import BaseModel
import httpx

router = APIRouter(prefix="/facebook", tags=["Facebook Ads"])

FB_API_URL = "https://graph.facebook.com/v22.0"

async def create_video_ad(account_id, adset_id, page_id, ad_name, video_id, thumbnail_hash, message, link, access_token):
    url = f"{FB_API_URL}/act_{account_id}/ads"

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
                        "value": {
                            "link": link
                        }
                    }
                }
            }
        },
        "status": "PAUSED"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            params={"access_token": access_token},
            json=payload
        )
        return response.json()