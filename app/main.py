from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import time

from app.database import Base, engine
from app.config import ALLOWED_ORIGINS, RATE_LIMIT_PER_MINUTE
from app.services.redis_service import redis_client

from app.routes.auth_routes import router as auth_router
from app.routes.chat_routes import router as chat_router
from app.routes.doctor_routes import router as doctor_router
from app.routes.appointment_routes import router as appointment_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ZuraAI Backend"
)

# 1. Rate Limiting Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for static files or non-api routes if needed
    if not request.url.path.startswith(("/chat", "/auth")):
        return await call_next(request)

    client_ip = request.client.host
    current_time = int(time.time())
    # Window-based rate limiting (1 minute)
    key = f"rate_limit:{client_ip}:{current_time // 60}"
    
    try:
        # Check if Redis is real or SimpleCache fallback
        if hasattr(redis_client, 'incr'):
            requests_count = redis_client.incr(key)
            if requests_count == 1:
                redis_client.expire(key, 60)
        else:
            # Fallback for SimpleCache (in-memory)
            requests_count = int(redis_client.get(key) or 0) + 1
            redis_client.set(key, requests_count, ex=60)
            
        if requests_count > RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please slow down and focus on your well-being."}
            )
    except Exception as e:
        print(f"Rate Limit Error: {e}")
        # Fail open to ensure user support isn't blocked by redis errors
        pass

    return await call_next(request)

# 2. CORS Hardening
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"PATH: {request.url.path} | TIME: {process_time:.4f}s")
    return response

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(doctor_router)
app.include_router(appointment_router)

@app.get("/")
def home():
    # Serve the index.html file from the root directory
    return FileResponse("index.html")