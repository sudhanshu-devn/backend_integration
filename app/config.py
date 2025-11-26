import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    FB_APP_ID: str = os.getenv("FB_APP_ID")
    FB_APP_SECRET: str = os.getenv("FB_APP_SECRET")
    FB_REDIRECT_URI: str = os.getenv("FB_REDIRECT_URI")
    FB_API_VERSION: str = os.getenv("FB_API_VERSION", "v23.0")

settings = Settings()