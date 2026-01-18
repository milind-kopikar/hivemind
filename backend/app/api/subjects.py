from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Subject
from ..schemas.schemas import SubjectResponse, SubjectBase

router = APIRouter()

@router.get("/", response_model=list[SubjectResponse])
def list_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).order_by(Subject.name).all()
    return subjects

@router.post("/", response_model=SubjectResponse)
def create_subject(payload: SubjectBase, db: Session = Depends(get_db)):
    existing = db.query(Subject).filter(Subject.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject already exists")
    s = Subject(name=payload.name)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s
