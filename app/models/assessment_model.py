from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    assessment_type = Column(String)  # stress, anxiety, depression, sleep, burnout
    score = Column(Integer)
    result_category = Column(String)  # e.g., "Low Stress", "Severe Anxiety"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserIntakeAssessment(Base):
    __tablename__ = "user_intake_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    q1 = Column(String)
    q2 = Column(String)
    q3 = Column(String)
    q4 = Column(String)
    q5 = Column(String)
    q6 = Column(String)
    q7 = Column(String)
    route_tier = Column(String) # Psychiatric, Psychological, Non-clinical, Premium
    route_layer = Column(String) # Mibo Main, MiboKids, etc.
    interest_tags = Column(String) # comma-separated tags
    privacy_preference = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
