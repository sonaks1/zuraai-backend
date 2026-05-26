from sqlalchemy import Column, Integer, String
from app.database import Base

class Appointment(Base):

    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer)

    doctor_id = Column(Integer)

    appointment_date = Column(String)

    status = Column(String)