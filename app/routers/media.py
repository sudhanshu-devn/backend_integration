import os
from fastapi import APIRouter, UploadFile, File, Form, Depends
from ..fb_api import upload_photo, upload_video
from ..auth import get_current_user

router = APIRouter(prefix="/media", tags=["Media"])

UPLOAD_FOLDER = "app/static/"
os.makedirs(f"{UPLOAD_FOLDER}/images", exist_ok=True)
os.makedirs(f"{UPLOAD_FOLDER}/videos", exist_ok=True)

@router.post("/upload", summary="Upload media to Facebook Page")
async def upload_media(
    file: UploadFile = File(...),
    caption: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """
    Uploads a file to the Facebook Page linked with the user.
    Returns the Facebook post ID (`create_id` equivalent).
    """
    ext = file.filename.split(".")[-1].lower()
    media_type = "image" if ext in ["jpg", "jpeg", "png"] else "video"

    save_path = os.path.join(UPLOAD_FOLDER, media_type + "s", file.filename)
    with open(save_path, "wb") as f:
        f.write(await file.read())

    fb_page_id = current_user["fb_page_id"]
    fb_token = current_user["fb_page_access_token"]

    if media_type == "image":
        resp = await upload_photo(fb_page_id, fb_token, save_path, caption)
    else:
        resp = await upload_video(fb_page_id, fb_token, save_path, caption)

    # Extract post id or return full response
    post_id = resp.get("id", resp)
    return {"create_id": post_id, "facebook_response": resp}