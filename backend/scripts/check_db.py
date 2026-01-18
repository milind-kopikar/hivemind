import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def check_connection():
    print(f"Attempting to connect to: {DATABASE_URL.split('@')[1]}")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            row = result.fetchone()
            print(f"Successfully connected to PostgreSQL!")
            print(f"Version: {row[0]}")
            
            # Check for pgvector
            try:
                res = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
                ext = res.fetchone()
                if ext:
                    print("pgvector extension is INSTALLED.")
                else:
                    print("pgvector extension is NOT installed in this database.")
            except Exception:
                print("Could not query extensions.")
                
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_connection()
