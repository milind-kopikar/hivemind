from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# pgvector is intentionally not required in production; use JSON fallback for embeddings
Vector = None

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    pseudo_name = Column(String, nullable=True)
    teacher = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notes = relationship("Note", back_populates="owner")
    analytics = relationship("StudentAnalytics", back_populates="student", uselist=False)

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)  # Structured Markdown from Gemini
    raw_image_url = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    chapter = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Use JSON for local testing. Replace with Vector(768) when pgvector is available.
    embedding = Column(JSON, nullable=True)

    owner = relationship("User", back_populates="notes")
    subject = relationship("Subject", back_populates="notes")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    notes = relationship("Note", back_populates="subject")

class MasterNote(Base):
    __tablename__ = "master_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    topic = Column(String, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    chapter = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Use JSON for local testing.
    embedding = Column(JSON, nullable=True)

    owner = relationship("User")

class StudentAnalytics(Base):
    __tablename__ = "student_analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    info_synthesis_score = Column(Float, default=0.0)
    peer_support_score = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    student = relationship("User", back_populates="analytics")
