from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base
from datetime import datetime

class MoodHistory(Base):
    __tablename__ = "mood_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    mood = Column(String)
    emotion = Column(String)
    severity = Column(Float, default=0.0)
    context = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class UserTrigger(Base):
    __tablename__ = "user_triggers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    trigger_name = Column(String) # e.g., "work stress", "family conflict"
    frequency = Column(Integer, default=1)
    last_detected = Column(DateTime, default=datetime.utcnow)

class WellnessProgress(Base):
    __tablename__ = "wellness_progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    exercise_id = Column(String) # e.g., "box_breathing"
    exercise_name = Column(String)
    completed_at = Column(DateTime, default=datetime.utcnow)
    feedback = Column(String, nullable=True) # How the user felt after