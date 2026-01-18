import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load backend/.env
base_dir = Path(__file__).resolve().parents[1]
env_path = base_dir / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

def migrate():
    with engine.connect() as conn:
        print("Starting migration to add pseudo_name, teacher, and year columns to 'users' table...")
        
        try:
            # Check if columns exist first to avoid errors (Postgres 9.6+ supports IF NOT EXISTS for columns in some ways but ALTER TABLE ADD COLUMN IF NOT EXISTS is standard in some dialects)
            # Actually for Postgres ADD COLUMN IF NOT EXISTS is supported since version 9.6
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS pseudo_name VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS teacher VARCHAR"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS year INTEGER"))
            print("Successfully updated 'users' table.")
        except Exception as e:
            print(f"Error updating 'users' table: {e}")
        
        conn.commit()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
