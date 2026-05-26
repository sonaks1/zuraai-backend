from sqlalchemy import Column, Integer, String
from app.database import Base

class Doctor(Base):

    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)

    name = Column(String)

    specialization = Column(String)

    experience = Column(String)

    available_time = Column(String)