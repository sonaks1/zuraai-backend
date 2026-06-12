from dotenv import load_dotenv
import os

# Set override=True to ensure values in .env take precedence over system environment variables
load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

# Production Hardening Config
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")