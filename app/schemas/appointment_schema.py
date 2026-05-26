from pydantic import BaseModel

class AppointmentSchema(BaseModel):

    doctor_id: int

    appointment_date: str