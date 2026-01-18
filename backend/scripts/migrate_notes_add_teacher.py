import sys
import os

# Add the parent directory to sys.path so we can import from 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine


def run_migration():
    print("Applying migration: add teacher column to notes table if not exists...")
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE notes ADD COLUMN IF NOT EXISTS teacher VARCHAR;"))
            conn.commit()
        print("Migration applied successfully.")
    except Exception as e:
        print("Migration failed:", e)


if __name__ == '__main__':
    run_migration()
