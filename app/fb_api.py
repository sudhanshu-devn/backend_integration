import httpx

GRAPH_API_URL = "https://graph.facebook.com/v17.0"

async def upload_photo(page_id: str, access_token: str, image_path: str, caption: str = ""):
    url = f"{GRAPH_API_URL}/{page_id}/photos"
    files = {"source": open(image_path, "rb")}
    data = {"caption": caption, "access_token": access_token}

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=data, files=files)
    return resp.json()

async def upload_video(page_id: str, access_token: str, video_path: str, description: str = ""):
    url = f"{GRAPH_API_URL}/{page_id}/videos"
    files = {"source": open(video_path, "rb")}
    data = {"description": description, "access_token": access_token}

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=data, files=files)
    return resp.json()