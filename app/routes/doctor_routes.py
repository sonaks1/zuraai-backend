from fastapi import APIRouter

router = APIRouter(
    prefix="/doctors"
)

@router.get("/")
def doctors():

    return [

        {
            "name":
            "Dr. Sarah",

            "specialization":
            "Psychologist"
        },

        {
            "name":
            "Dr. John",

            "specialization":
            "Therapist"
        }
    ]