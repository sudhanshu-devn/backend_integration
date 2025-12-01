import httpx
from fastapi import HTTPException

FB_API_URL = "https://graph.facebook.com/v22.0"
VALID_OBJECTIVES = [
    "APP_INSTALLS", "BRAND_AWARENESS", "EVENT_RESPONSES", "LEAD_GENERATION",
    "LINK_CLICKS", "LOCAL_AWARENESS", "MESSAGES", "OFFER_CLAIMS", "PAGE_LIKES",
    "POST_ENGAGEMENT", "PRODUCT_CATALOG_SALES", "REACH", "STORE_VISITS",
    "VIDEO_VIEWS", "OUTCOME_AWARENESS", "OUTCOME_ENGAGEMENT", "OUTCOME_LEADS",
    "OUTCOME_SALES", "OUTCOME_TRAFFIC", "OUTCOME_APP_PROMOTION", "CONVERSIONS"
]

async def create_campaign(account_id: str, name: str, objective: str, access_token: str, special_ad_categories=None):
    # Default to NONE if not provided
    if special_ad_categories is None:
        special_ad_categories = ["NONE"]

    if objective not in VALID_OBJECTIVES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid objective '{objective}'. Must be one of: {', '.join(VALID_OBJECTIVES)}"
        )

    url = f"{FB_API_URL}/act_{account_id}/campaigns"

    payload = {
        "name": name,
        "objective": objective,
        "status": "PAUSED",
        "special_ad_categories": special_ad_categories
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            params={"access_token": access_token},
            json=payload,
            timeout=30
        )

    data = response.json()

    # Handle Facebook API errors
    if "error" in data:
        # **Use the full message from Facebook for better debugging**
        facebook_error_message = data['error'].get('message', 'Unknown Facebook Error')
        
        # Include the error code and type for completeness
        error_code = data['error'].get('code', 'N/A')
        error_type = data['error'].get('type', 'N/A')
        
        raise HTTPException(
            status_code=400,
            detail=f"Facebook API Error ({error_type} {error_code}): {facebook_error_message}"
        )
    
    return data
