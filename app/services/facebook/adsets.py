import httpx

FB_API_URL = "https://graph.facebook.com/v22.0"

async def create_adset(account_id, campaign_id, name, daily_budget, start, end, access_token):
    url = f"{FB_API_URL}/act_{account_id}/adsets"

    payload = {
        "name": name,
        "campaign_id": campaign_id,
        "daily_budget": daily_budget,
        "start_time": start,
        "end_time": end,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "REACH",
        "status": "PAUSED"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            params={"access_token": access_token},
            json=payload
        )
        return response.json()
