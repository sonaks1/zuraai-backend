from sqlalchemy import Column, Integer, String
from app.database import Base

class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer)

    message = Column(String)

    response = Column(String)

    emotion = Column(String)