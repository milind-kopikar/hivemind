from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    pseudo_name: str
    teacher: str
    year: int

class UserLogin(UserBase):
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(UserBase):
    id: int
    created_at: datetime
    pseudo_name: Optional[str] = None
    teacher: Optional[str] = None
    year: Optional[int] = None

    class Config:
        from_attributes = True

class NoteBase(BaseModel):
    content: str
    raw_image_url: Optional[str] = None
    subject_id: int
    chapter: int

class NoteCreate(NoteBase):
    pass

class NoteResponse(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    # New fields for frontend list
    pseudo_name: Optional[str] = None
    teacher: Optional[str] = None
    year: Optional[int] = None

    class Config:
        from_attributes = True

class SubjectBase(BaseModel):
    name: str

class SubjectResponse(SubjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MasterNoteBase(BaseModel):
    topic: str
    content: str
    version: int

class MasterNoteResponse(MasterNoteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    info_synthesis_score: float
    peer_support_score: float
    last_updated: Optional[datetime]

    class Config:
        from_attributes = True

class TutorRequest(BaseModel):
    subject_id: int
    chapter: int
    question: str
    mode: str = "chat"

class ConsensusRequest(BaseModel):
    subject_id: int
    chapter: Optional[int] = None
    note_ids: List[int]
