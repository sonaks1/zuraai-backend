from sqlalchemy import text
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
    print("- Verified/Created all tables (user_triggers, wellness_progress, etc.)")

    with engine.connect() as conn:
        try:
            # Fix users table
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS visitor_id VARCHAR;"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR;"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS preferred_language VARCHAR DEFAULT 'English';"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS support_preference VARCHAR;"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS premium_status BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS tier VARCHAR;"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_layer VARCHAR;"))
            
            conn.execute(text("ALTER TABLE users ALTER COLUMN phone DROP NOT NULL;"))
            conn.execute(text("ALTER TABLE users ALTER COLUMN email DROP NOT NULL;"))
            conn.execute(text("ALTER TABLE users ALTER COLUMN password DROP NOT NULL;"))
            print("- Verified 'users' table columns")

            # Fix chat_history table
            conn.execute(text("ALTER TABLE chat_history ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
            print("- Verified 'chat_history' table columns (added timestamp)")

            # Fix mood_history table
            conn.execute(text("ALTER TABLE mood_history ADD COLUMN IF NOT EXISTS severity FLOAT DEFAULT 0.0;"))
            conn.execute(text("ALTER TABLE mood_history ADD COLUMN IF NOT EXISTS context TEXT;"))
            conn.execute(text("ALTER TABLE mood_history ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
            print("- Verified 'mood_history' table columns (added severity, context, timestamp)")
            
            conn.commit()
            print("Database schema updated successfully!")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    fix_database()
