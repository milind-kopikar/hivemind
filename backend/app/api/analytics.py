from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Note, User
from ..core.security import get_current_user

router = APIRouter()

@router.get("/report")
async def get_analytics(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user.get("sub")
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        return {"prep_score": 0, "contribution_score": 0}

    # Contribution Score: Simple count of notes uploaded
    note_count = db.query(Note).filter(Note.user_id == user.id).count()
    # Normalize score: say 10 notes = 100% contribution level for the month
    contribution_score = min(100, note_count * 10)

    # Prep Score: Mocked for now, in a real app would be from quiz_attempts table
    prep_score = 75 # placeholder

    return {
        "prep_score": prep_score,
        "contribution_score": contribution_score,
        "prep_level": 3 if prep_score > 50 else 1
    }
