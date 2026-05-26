from pydantic import BaseModel
from typing import Optional

class RegisterSchema(BaseModel):
    name: str
    phone: str

class LoginSchema(BaseModel):
    phone: str

class VerifyOTPSchema(BaseModel):
    phone: str
    otp: str