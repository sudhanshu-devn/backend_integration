from fastapi import APIRouter, UploadFile, File, HTTPException
from app.storage import get_user

router = APIRouter(prefix="/media", tags=["Media"])


@router.post("/upload")
async def upload_media(user_id: str, file: UploadFile = File(...)):
    user = get_user(user_id)
    if not user:
        raise HTTPException(401, "User not authenticated with Facebook")

    return {
        "status": "received",
        "filename": file.filename,
        "user_id": user_id,
    }
