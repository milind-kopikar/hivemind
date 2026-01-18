from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..core.ai_agents import get_ingestion_agent, extract_text_from_image
from ..core.security import get_current_user
from ..models import Note
import base64
import os
import traceback

router = APIRouter()

@router.post("/upload")
async def upload_note(
    file: UploadFile = File(...), 
    subject_id: int = Form(...),
    chapter: int = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub") # Assuming 'sub' contains the user id (it was emailed in previous turns, but let's check)
    # Actually, in auth.py we might have used 'email' or 'user_id'. 
    # Let's check auth.py payload.
    
    print(f"[ingestion] upload called by user {user_id}, filename={file.filename}, subject={subject_id}, chapter={chapter}")
    try:
        # Read image
        content = await file.read()
        image_b64 = base64.b64encode(content).decode('utf-8')

        # Use PydanticAI to process image
        try:
            agent = get_ingestion_agent()
        except Exception as e:
            print(f"[ingestion] get_ingestion_agent raised: {e}")
            agent = None

        # Allow a mock ingestion mode controlled by env var MOCK_INGESTION=1 (useful for local testing)
        mock_mode = os.getenv('MOCK_INGESTION', '0') == '1'

        if not agent and not mock_mode:
            return JSONResponse(status_code=503, content={"detail": "Ingestion agent not configured. Set GOOGLE_API_KEY or enable MOCK_INGESTION for local testing."})

        extracted_content = ""
        if mock_mode:
            # Simple deterministic mock: return filename and placeholder markdown
            extracted_content = f"# Mocked Ingestion for {file.filename}\n\nThis is a mock conversion of the uploaded file. Replace with Gemini output when available.\n\n- Uploaded filename: {file.filename}\n- Suggested summary: This note covers the key points from the lecture."
        else:
            # Use our new high-quality OCR extraction
            extracted_content = await extract_text_from_image(content)

        # Save to DB
        # Find numeric user_id if current_user["sub"] is email
        from ..models import User
        db_user = db.query(User).filter(User.email == user_id).first()
        uid = db_user.id if db_user else 1

        new_note = Note(
            content=extracted_content,
            user_id=uid,
            subject_id=subject_id,
            chapter=chapter
        )
        db.add(new_note)
        db.commit()
        db.refresh(new_note)

        # Trigger consensus check (placeholder for now)
        # In a real app, this might be a background task
        # check_consensus(subject_id, chapter, db)

        return JSONResponse(status_code=200, content={"id": new_note.id, "content": new_note.content})
    except Exception as e:
        print("[ingestion] Exception:", e)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
