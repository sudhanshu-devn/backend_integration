import httpx

FB_API_URL = "https://graph.facebook.com/v22.0"

async def create_ad(account_id, adset_id, page_id, ad_name, image_hash, message, link, access_token):
    url = f"{FB_API_URL}/act_{account_id}/ads"

    payload = {
        "name": ad_name,
        "adset_id": adset_id,
        "creative": {
            "object_story_spec": {
                "page_id": page_id,
                "link_data": {
                    "message": message,
                    "link": link,
                    "image_hash": image_hash
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