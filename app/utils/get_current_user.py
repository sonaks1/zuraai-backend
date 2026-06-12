from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.config import JWT_SECRET
from app.database import SessionLocal
from app.models.user_model import User

security = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

def get_current_user(
    token=Depends(security),
    db: Session = Depends(get_db)
):
    if not token or not token.credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a Bearer token."
        )

    try:
        payload = jwt.decode(
            token.credentials,
            JWT_SECRET,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user_id"
            )

        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication error"
        )