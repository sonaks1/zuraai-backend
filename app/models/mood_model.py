from sqlalchemy import Column, Integer, String
from app.database import Base

class MoodHistory(Base):

    __tablename__ = "mood_history"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer)

    mood = Column(String)

    emotion = Column(String)

    date = Column(String)