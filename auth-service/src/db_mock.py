from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS_DB = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "hashed_password": pwd_context.hash("secret123"),
        "disabled": False
    },
    "janesmith": {
        "username": "janesmith",
        "full_name": "Jane Smith",
        "email": "jane.smith@example.com",
        "hashed_password": pwd_context.hash("mypassword"),
        "disabled": False
    }
}

def get_user(username: str):
    return USERS_DB.get(username)

def get_all_users():
    return list(USERS_DB.values())
