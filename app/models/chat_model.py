from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    message = Column(String)
    response = Column(String)
    emotion = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)