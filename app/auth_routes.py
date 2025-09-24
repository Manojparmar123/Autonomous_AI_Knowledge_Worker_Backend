from fastapi import APIRouter, Depends, HTTPException, Body, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

from .config import settings
from .auth import current_user

router = APIRouter(tags=["auth"])

# --- Email configuration --- #
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True
)
fm = FastMail(conf)

# --- JWT & Password utilities --- #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

# --- In-memory user store for demo --- #
users_db = {}

# --- Request models --- #
class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# --- Signup endpoint --- #
@router.post("/signup")
async def signup(req: SignupRequest):
    if req.email in users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed = hash_password(req.password)
    users_db[req.email] = {"email": req.email, "password": hashed}
    return {"msg": "User registered successfully"}

# --- Login endpoint --- #
@router.post("/login")
async def login(req: LoginRequest):
    user = users_db.get(req.email)
    if user and verify_password(req.password, user["password"]):
        token = create_access_token({"sub": req.email})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# --- Forgot password endpoint --- #
@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    user = users_db.get(req.email)
    if not user:
        # Do not reveal whether email exists
        return {"msg": f"If an account with {req.email} exists, a password reset link has been sent."}

    reset_token = create_access_token({"sub": req.email}, expires_delta=timedelta(minutes=15))
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    message = MessageSchema(
        subject="Reset your password",
        recipients=[req.email],
        body=f"Click this link to reset your password (valid for 15 minutes): {reset_link}",
        subtype="plain"
    )

    try:
        await fm.send_message(message)
        return {"msg": f"If an account with {req.email} exists, a password reset link has been sent."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send email: {str(e)}")

# --- Reset password endpoint --- #
@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    try:
        payload = jwt.decode(req.token, settings.JWT_SECRET, algorithms=["HS256"])
        email: str = payload.get("sub")
        if not email or email not in users_db:
            raise HTTPException(status_code=400, detail="Invalid token")
        users_db[email]["password"] = hash_password(req.new_password)
        return {"msg": "Password reset successfully"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

# --- Get current user info --- #
@router.get("/me")
def get_me(user=Depends(current_user)):
    return user
