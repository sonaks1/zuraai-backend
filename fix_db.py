from sqlalchemy import text, inspect
from app.database import engine, Base
# Import models to ensure they are registered with Base.metadata
from app.models.user_model import User
from app.models.chat_model import ChatHistory
from app.models.mood_model import MoodHistory, UserTrigger, WellnessProgress
from app.models.assessment_model import AssessmentResult, UserIntakeAssessment
from app.models.appointment_model import Appointment
from app.models.doctor_model import Doctor

def fix_database():
    print("Connecting to database to fix schema...")
    
    # Ensure new tables are created
    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        try:
            # 1. Fix users table columns
            columns = [c['name'] for c in inspector.get_columns('users')]
            
            if 'visitor_id' not in columns:
                print("- Adding 'visitor_id' to users")
                conn.execute(text("ALTER TABLE users ADD COLUMN visitor_id VARCHAR;"))
            
            if 'phone' not in columns:
                print("- Adding 'phone' to users")
                conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR;"))
            
            # Add other missing columns
            for col in ['onboarding_completed', 'preferred_language', 'support_preference', 'premium_status', 'tier', 'onboarding_layer']:
                if col not in columns:
                    print(f"- Adding '{col}' to users")
                    type_str = "BOOLEAN DEFAULT FALSE" if "status" in col or "completed" in col else "VARCHAR"
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {type_str};"))

            # 2. Fix chat_history
            columns_chat = [c['name'] for c in inspector.get_columns('chat_history')]
            if 'timestamp' not in columns_chat:
                print("- Adding 'timestamp' to chat_history")
                conn.execute(text("ALTER TABLE chat_history ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))

            # 3. Fix mood_history
            columns_mood = [c['name'] for c in inspector.get_columns('mood_history')]
            if 'severity' not in columns_mood:
                print("- Adding 'severity' to mood_history")
                conn.execute(text("ALTER TABLE mood_history ADD COLUMN severity FLOAT DEFAULT 0.0;"))
            if 'context' not in columns_mood:
                print("- Adding 'context' to mood_history")
                conn.execute(text("ALTER TABLE mood_history ADD COLUMN context TEXT;"))
            
            conn.commit()
            print("Database schema updated successfully!")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    fix_database()
