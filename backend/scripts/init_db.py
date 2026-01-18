import sys
import os

# Add the parent directory to sys.path so we can import from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, Base
from app.models import User, Note, MasterNote, StudentAnalytics # Ensure models are loaded

def init_db():
    print("Connecting to database to initialize...")
    try:
        with engine.connect() as conn:
            # Enable pgvector extension
            print("Enabling pgvector extension...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
            print("Extension 'vector' is ready.")

        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("\nNote: Make sure your local PostgreSQL server is running and the 'hivemind' database exists.")
        print("If you get a 'vector' extension error, you may need to install pgvector on your local machine.")

if __name__ == "__main__":
    init_db()
