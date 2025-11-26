import requests

def get_user_ad_accounts(access_token: str):
    """
    Fetch all Facebook Ad Accounts for a user using their access token.
    """
    url = "https://graph.facebook.com/v23.0/me/adaccounts"
    params = {
        "access_token": access_token,
        "limit": 600,
        "fields": (
            "name,account_id,account_status,disable_reason,"
            "timezone_id,timezone_name,timezone_offset_hours_utc,"
            "currency,id"
        )
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()  # JSON with ad accounts
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
