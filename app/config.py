from dotenv import load_dotenv
import os

# Set override=True to ensure values in .env take precedence over system environment variables
load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

JWT_SECRET = os.getenv("JWT_SECRET")