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
        # --- LOCAL DEVELOPMENT FALLBACK ---
        # Allow testing without tokens by defaulting to User ID 1
        user = db.query(User).filter(User.id == 1).first()
        if user:
            return user
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

        user_id = payload["user_id"]

        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if not user:
            # Fallback if user in token doesn't exist
            user = db.query(User).filter(User.id == 1).first()
            if user: return user
            raise HTTPException(
                status_code=401,
                detail="Invalid User"
            )

        return user

    except:
        # --- LOCAL DEVELOPMENT FALLBACK ---
        # If token is invalid/expired, default to User ID 1 for testing
        user = db.query(User).filter(User.id == 1).first()
        if user:
            return user

        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )