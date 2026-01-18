import sqlalchemy
from sqlalchemy import create_engine, text
import sys

def check_db_info():
    # Use the postgres user from .env to inspect the db
    url = "postgresql://postgres:password@localhost:5432/postgres"
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            print("Connected to postgres as 'postgres' user.")
            
            # Check if hivemind db exists
            result = conn.execute(text("SELECT datname FROM pg_database WHERE datname = 'hivemind';"))
            if result.fetchone():
                print("Database 'hivemind' exists.")
            else:
                print("Database 'hivemind' does NOT exist.")
                
            # Check if milind user exists
            result = conn.execute(text("SELECT usename FROM pg_user WHERE usename = 'milind';"))
            if result.fetchone():
                print("User 'milind' exists.")
            else:
                print("User 'milind' does NOT exist.")
                
            # Check extensions in hivemind if it exists
            try:
                hivemind_engine = create_engine("postgresql://postgres:password@localhost:5432/hivemind")
                with hivemind_engine.connect() as hconn:
                    print("Connected to 'hivemind' as 'postgres' user.")
                    result = hconn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
                    if result.fetchone():
                        print("Vector extension is AVAILABLE in 'hivemind'.")
                    else:
                        print("Vector extension is NOT AVAILABLE in 'hivemind'.")
            except Exception as e:
                print(f"Could not connect to 'hivemind' database: {e}")

    except Exception as e:
        print(f"Failed to connect as postgres. Error: {e}")

if __name__ == "__main__":
    check_db_info()
