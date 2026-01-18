import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Add the current directory to sys.path so we can find things if needed
sys.path.append(os.getcwd())

# Load environment variables
env_path = Path("backend/.env")
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not found in backend/.env")
    sys.exit(1)

# Ensure the URL is one SQLAlchemy can use (sometimes need to replace postgres:// with postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

tables_to_clear = [
    "student_analytics",
    "notes",
    "master_notes",
    "users"
]

def clear_db():
    try:
        with engine.connect() as connection:
            # Start a transaction
            with connection.begin():
                for table in tables_to_clear:
                    print(f"Deleting all records from {table}...")
                    # Using TRUNCATE CASCADE might be better but let's stick to DELETE as requested
                    # and provided order should respect foreign keys.
                    connection.execute(text(f"DELETE FROM {table}"))
                print("All records deleted successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clear_db()
