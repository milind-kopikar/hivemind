from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import text
from ..database import engine
import os

router = APIRouter()

@router.post('/run-migration-notes-teacher')
async def run_migration(admin_secret: str | None = Header(None)):
    """Run the migration to add `teacher` column to `notes` table.
    This endpoint is protected by the app's SECRET_KEY via the `Admin-Secret` header.
    It is intended to be a short-lived admin utility."
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise HTTPException(status_code=500, detail='Server SECRET_KEY not configured')
    if admin_secret != SECRET_KEY:
        raise HTTPException(status_code=401, detail='Unauthorized')

    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE notes ADD COLUMN IF NOT EXISTS teacher VARCHAR;"))
            conn.commit()
        return {"status": "ok", "message": "Migration applied (notes.teacher added if missing)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
