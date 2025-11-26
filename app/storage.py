# Replace this with real DB later
USER_STORE = {}  # {user_id: {access_token, email, name}}

def save_user(user_id: str, data: dict):
    USER_STORE[user_id] = data

def get_user(user_id: str):
    return USER_STORE.get(user_id)