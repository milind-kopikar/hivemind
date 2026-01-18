from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Note, User, Subject
from ..schemas.schemas import NoteResponse
from typing import Optional
from ..core.security import decode_access_token

router = APIRouter()


def get_current_user_from_header(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    scheme, _, token = authorization.partition(" ")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.email == payload.get('sub')).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.get("/all", response_model=list[NoteResponse])
def all_notes(subject_id: int, chapter: Optional[int] = None, db: Session = Depends(get_db)):
    """Fetch all notes for a specific subject (and optionally a chapter), including user metadata."""
    query = db.query(Note, User.pseudo_name, User.teacher, User.year)\
              .join(User, Note.user_id == User.id)\
              .filter(Note.subject_id == subject_id)
    
    if chapter is not None and chapter > 0:
        query = query.filter(Note.chapter == chapter)
        
    notes = query.order_by(User.teacher, User.year.desc(), User.pseudo_name).all()
    
    # Map the join result to a list of NoteResponse compatible objects
    results = []
    for note, p_name, teacher, year in notes:
        n_dict = {
            "id": note.id,
            "content": note.content,
            "user_id": note.user_id,
            "subject_id": note.subject_id,
            "chapter": note.chapter,
            "created_at": note.created_at,
            "pseudo_name": p_name,
            "teacher": teacher,
            "year": year
        }
        results.append(NoteResponse(**n_dict))
    return results

@router.get("/my", response_model=list[NoteResponse])
def my_notes(subject_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_header)):
    q = db.query(Note).filter(Note.user_id == current_user.id)
    if subject_id:
        q = q.filter(Note.subject_id == subject_id)
    # Order by chapter asc, then created_at asc
    q = q.order_by(Note.chapter.asc().nulls_last(), Note.created_at.asc())
    return q.all()
