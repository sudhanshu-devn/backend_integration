from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.advideo import AdVideo

def upload_media_service(account_id: str, media_type: str, access_token: str, temp_path: str):
    FacebookAdsApi.init(access_token=access_token)

    if media_type.lower() == "image":
        image = AdImage(parent_id=account_id)
        image[AdImage.Field.filename] = temp_path
        image.remote_create()
        return {"image_hash": image[AdImage.Field.hash]}

    elif media_type.lower() == "video":
        video = AdVideo(parent_id=account_id)
        video[AdVideo.Field.filepath] = temp_path
        video.remote_create()
        return {"video_id": video[AdVideo.Field.id]}

    else:
        return {"error": "Invalid media_type. Must be 'image' or 'video'."}
