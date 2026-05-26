from fastapi import APIRouter

router = APIRouter(
    prefix="/appointments"
)

@router.post("/book")
def book():

    return {
        "message":
        "Appointment Booked"
    }