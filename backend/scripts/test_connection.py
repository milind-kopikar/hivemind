import sqlalchemy
from sqlalchemy import create_engine, text
import sys

def test_connection(user, password, host, port, dbname):
    url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            print(f"Successfully connected to {dbname} as {user} with password: '{password}'")
            
            # Check for vector extension
            result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
            extension = result.fetchone()
            if extension:
                print("Vector extension is AVAILABLE.")
            else:
                print("Vector extension is NOT AVAILABLE.")
            return True
    except Exception as e:
        print(f"Failed to connect as {user} with password: '{password}'. Error: {e}")
        return False

if __name__ == "__main__":
    db_name = "hivemind"
    user = "milind"
    host = "localhost"
    port = "5432"
    
    passwords = ["", "password"]
    
    success = False
    for pwd in passwords:
        if test_connection(user, pwd, host, port, db_name):
            success = True
            break
            
    if not success:
        sys.exit(1)
