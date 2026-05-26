from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

from app.database import Base, engine

from app.routes.auth_routes import router as auth_router
from app.routes.chat_routes import router as chat_router
from app.routes.doctor_routes import router as doctor_router
from app.routes.appointment_routes import router as appointment_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ZuraAI Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(doctor_router)
app.include_router(appointment_router)

@app.get("/")
def home():
    # Serve the index.html file from the root directory
    return FileResponse("index.html")