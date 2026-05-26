from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user_model import User

from app.schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    VerifyOTPSchema
)

from app.utils.jwt_handler import (
    create_token
)

router = APIRouter(
    prefix="/auth"
)

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# Mock OTP storage (Phone -> OTP)
# In production, use Redis or a database
temp_otp_storage = {}

@router.post("/request-otp")
def request_otp(
    data: RegisterSchema,
    db: Session = Depends(get_db)
):
    # Check if user exists, if not create them (as per user description "login with phone and name")
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        user = User(name=data.name, phone=data.phone)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Mock sending OTP
    otp = "123456" # Hardcoded for demo
    temp_otp_storage[data.phone] = otp
    
    print(f"DEBUG: OTP for {data.phone} is {otp}")

    return {
        "message": "Verification code sent to your phone"
    }

@router.post("/verify-otp")
def verify_otp(
    data: VerifyOTPSchema,
    db: Session = Depends(get_db)
):
    stored_otp = temp_otp_storage.get(data.phone)
    
    if not stored_otp or data.otp != stored_otp:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_token(user.id)
    
    # Clear OTP after use
    if data.phone in temp_otp_storage:
        del temp_otp_storage[data.phone]

    return {
        "access_token": token,
        "user_id": user.id,
        "name": user.name
    }

@router.post("/register")
def register(
    data: RegisterSchema,
    db: Session = Depends(get_db)
):
    # Keep it for compatibility but redirect to request-otp logic
    return request_otp(data, db)

@router.post("/login")
def login(
    data: LoginSchema,
    db: Session = Depends(get_db)
):
    # Mocking login as just requesting OTP if we only have phone
    # In this flow, login/register are merged into request-otp
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        return {"error": "User not found. Please register with name and phone."}
    
    # Mock sending OTP
    otp = "123456"
    temp_otp_storage[data.phone] = otp
    return {"message": "Verification code sent"}