from app.database import engine, Base
from app.services.redis_service import redis_client
from app.vector_memory.chroma_db import collection
import redis

# Import all models to ensure Base.metadata is fully populated
from app.models.user_model import User
from app.models.chat_model import ChatHistory
from app.models.mood_model import MoodHistory, UserTrigger, WellnessProgress
from app.models.assessment_model import AssessmentResult, UserIntakeAssessment
from app.models.appointment_model import Appointment
from app.models.doctor_model import Doctor

def cleanup_data():
    print("WARNING: This will delete ALL user data, chat history, and settings.")
    
    # 1. Clear SQL Database
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Recreating all tables...")
    Base.metadata.create_all(bind=engine)
    print("SQL Database reset successfully.")

    # 2. Clear Redis
    print("Clearing Redis cache/sessions...")
    try:
        if isinstance(redis_client, redis.Redis):
            redis_client.flushall()
            print("Redis flushed successfully.")
        else:
            # SimpleCache fallback
            redis_client.data = {}
            print("In-memory cache cleared successfully.")
    except Exception as e:
        print(f"Error clearing Redis: {e}")

    # 3. Clear ChromaDB (Vector Memory)
    print("Clearing Vector Memory (ChromaDB)...")
    try:
        # Get all IDs and delete them
        all_data = collection.get()
        if all_data['ids']:
            collection.delete(ids=all_data['ids'])
            print(f"Deleted {len(all_data['ids'])} memory vectors.")
        else:
            print("Vector memory was already empty.")
    except Exception as e:
        print(f"Error clearing ChromaDB: {e}")

    print("Cleanup complete. All data has been deleted.")

if __name__ == "__main__":
    cleanup_data()
