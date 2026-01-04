from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import psycopg2
from psycopg2 import OperationalError

# --- FastAPI app ---
app = FastAPI(title="Auth Service", version="1.0")

# --- JWT and password config ---
SECRET_KEY = "supersecretkey123"  # use env vars in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- In-memory mock DB ---
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

# --- Helper functions for mock DB ---
def get_user_mock(username: str):
    return USERS_DB.get(username)

def get_all_users_mock():
    return list(USERS_DB.values())

# --- Attempt to connect to Postgres ---
try:
    conn = psycopg2.connect(
        host="newbank-db",  # or container name
        database="postgres",
        user="postgres",
        password="supersecret",
        port=5432
    )
    POSTGRES_AVAILABLE = True
except OperationalError:
    conn = None
    POSTGRES_AVAILABLE = False
    print("⚠️  Postgres not available, falling back to mock DB")

# --- Pydantic models ---
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool = False

# --- Health endpoint ---
@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}

# --- Users endpoint ---
@app.get("/users")
def users():
    if POSTGRES_AVAILABLE:
        cur = conn.cursor()
        cur.execute("SELECT username, full_name, email, disabled FROM users")
        rows = cur.fetchall()
        cur.close()
        return [
            {"username": u[0], "full_name": u[1], "email": u[2], "disabled": u[3]}
            for u in rows
        ]
    else:
        return [
            {"username": u["username"], "full_name": u["full_name"],
             "email": u["email"], "disabled": u["disabled"]}
            for u in get_all_users_mock()
        ]

# --- Login endpoint ---
@app.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    if POSTGRES_AVAILABLE:
        cur = conn.cursor()
        cur.execute(
            "SELECT username, hashed_password, disabled FROM users WHERE username = %s",
            (request.username,)
        )
        user_row = cur.fetchone()
        cur.close()
        if not user_row:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        username, hashed_password, disabled = user_row
    else:
        user = get_user_mock(request.username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        username = user["username"]
        hashed_password = user["hashed_password"]
        disabled = user["disabled"]

    if not pwd_context.verify(request.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if disabled:
        raise HTTPException(status_code=403, detail="User is disabled")

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload = {"sub": username, "exp": expire}
    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}
