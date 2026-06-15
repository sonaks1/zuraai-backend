from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    visitor_id = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=True)
    onboarding_completed = Column(Boolean, default=False)
    
    preferred_language = Column(String, default="English")
    support_preference = Column(String, nullable=True) # e.g., "Text-only", "Open"
    premium_status = Column(Boolean, default=False)
    tier = Column(String, nullable=True) # Psychiatric, Psychological, Non-clinical, Premium
    onboarding_layer = Column(String, nullable=True) # Mibo Main, MiboKids, etc.