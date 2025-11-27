import httpx

FB_API_URL = "https://graph.facebook.com/v22.0"

async def create_adset(account_id, campaign_id, name, daily_budget, start_time, end_time, access_token, targeting=None):
    url = f"{FB_API_URL}/act_{account_id}/adsets"

    # Default targeting if none provided
    if targeting is None:
        targeting = {
            "geo_locations": {"countries": ["US"]},  # minimum required
            "age_min": 18,
            "age_max": 65,
            "genders": [1, 2]
        }

    payload = {
        "name": name,
        "campaign_id": campaign_id,
        "daily_budget": daily_budget * 100,  # Facebook expects amount in cents
        "start_time": start_time,
        "end_time": end_time,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "REACH",
        "status": "PAUSED",
        "targeting": targeting,
        "bid_amount": 200,  # in cents, e.g., $2.00
        # "bid_strategy": "LOWEST_COST_WITHOUT_CAP"  # automatic bidding
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            params={"access_token": access_token},
            json=payload
        )
        return response.json()