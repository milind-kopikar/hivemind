import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")
db_url = os.getenv("DATABASE_URL")

engine = create_engine(db_url)

def migrate():
    with engine.connect() as conn:
        print("Starting migration to add subject_id and chapter columns...")
        
        # Add columns to 'notes' table
        try:
            conn.execute(text("ALTER TABLE notes ADD COLUMN IF NOT EXISTS subject_id INTEGER REFERENCES subjects(id)"))
            conn.execute(text("ALTER TABLE notes ADD COLUMN IF NOT EXISTS chapter INTEGER"))
            print("Successfully updated 'notes' table.")
        except Exception as e:
            print(f"Error updating 'notes' table: {e}")

        # Add columns to 'master_notes' table
        try:
            conn.execute(text("ALTER TABLE master_notes ADD COLUMN IF NOT EXISTS subject_id INTEGER REFERENCES subjects(id)"))
            conn.execute(text("ALTER TABLE master_notes ADD COLUMN IF NOT EXISTS chapter INTEGER"))
            print("Successfully updated 'master_notes' table.")
        except Exception as e:
            print(f"Error updating 'master_notes' table: {e}")
        
        conn.commit()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
