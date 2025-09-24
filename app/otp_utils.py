import random

otp_storage = {}  # In-memory, for production use DB

def generate_otp(email: str) -> str:
    otp = str(random.randint(100000, 999999))
    otp_storage[email] = otp
    return otp

def verify_otp(email: str, otp: str) -> bool:
    return otp_storage.get(email) == otp
