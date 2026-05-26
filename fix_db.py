from sqlalchemy import text
from app.database import engine

def fix_database():
    print("Connecting to database to fix schema...")
    with engine.connect() as conn:
        try:
            # Add phone column
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR;"))
            print("- Added 'phone' column (or it already existed)")
            
            # Make email nullable
            conn.execute(text("ALTER TABLE users ALTER COLUMN email DROP NOT NULL;"))
            print("- Made 'email' nullable")
            
            # Make password nullable
            conn.execute(text("ALTER TABLE users ALTER COLUMN password DROP NOT NULL;"))
            print("- Made 'password' nullable")
            
            conn.commit()
            print("Database schema updated successfully!")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    fix_database()
