import requests
import httpx

FB_GRAPH_URL = "https://graph.facebook.com/v24.0"

async def fb_get(path: str, params: dict):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FB_GRAPH_URL}/{path}", params=params)
        return response.json()

def fb_post(path: str, payload: dict):
    url = f"{FB_GRAPH_URL}/{path}"
    return requests.post(url, data=payload).json()
