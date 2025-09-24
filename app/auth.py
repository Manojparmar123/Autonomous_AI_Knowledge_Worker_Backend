from fastapi import APIRouter, HTTPException, Header, Depends, Body, status
from typing import Optional
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

# Load environment variables
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "your_secret_key")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")
    return encoded_jwt

def get_current_user_jwt(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {
            "email": payload.get("sub"),
            "role": payload.get("role", "analyst")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def current_user(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    return get_current_user_jwt(authorization)

# ✅ New helper for role-based access
def require_role(required_role: str):
    def role_checker(user: dict = Depends(current_user)):
        if user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Forbidden: insufficient permissions")
        return user
    return role_checker

# ---------------- APIRouter ----------------
router = APIRouter()

@router.post("/login")
def login(email: str = Body(...), password: str = Body(...)):
    """
    Dummy authentication for demo:
    - admin@example.com → Admin
    - user@example.com  → Analyst
    """
    if email == "admin@example.com" and password == "adminpass":
        access_token = create_access_token({"sub": email, "role": "admin"})
        return {"access_token": access_token, "token_type": "bearer", "role": "admin"}

    if email == "user@example.com" and password == "password":
        access_token = create_access_token({"sub": email, "role": "analyst"})
        return {"access_token": access_token, "token_type": "bearer", "role": "analyst"}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@router.post("/forgot-password")
def forgot_password(email: str = Body(...)):
    return {
        "status": "success",
        "message": f"If an account with {email} exists, a password reset link has been sent."
    }

@router.get("/me")
def read_current_user(user: dict = Depends(current_user)):
    return user

# ✅ Example protected route
@router.get("/admin-only")
def admin_dashboard(user: dict = Depends(require_role("admin"))):
    return {"message": f"Welcome Admin {user['email']}"}

@router.get("/analyst-only")
def analyst_dashboard(user: dict = Depends(require_role("analyst"))):
    return {"message": f"Welcome Analyst {user['email']}"}
