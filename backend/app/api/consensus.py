from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Note, MasterNote, Subject, User
from ..core.ai_agents import get_consensus_agent
from ..schemas.schemas import ConsensusRequest
from ..core.security import decode_access_token
import json
from typing import Optional

router = APIRouter()

def get_current_user_id(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    payload = decode_access_token(token)
    if not payload:
        return None
    user = db.query(User).filter(User.email == payload.get('sub')).first()
    return user.id if user else None

@router.post("/process")
async def run_consensus_v2(
    payload: ConsensusRequest, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    # 1. Gather ONLY selected notes
    notes = db.query(Note).filter(Note.id.in_(payload.note_ids)).all()
    
    if not notes:
        raise HTTPException(status_code=400, detail="No notes selected for consensus")

    # If chapter is not provided, try to infer it from the first note, or default to 1
    target_chapter = payload.chapter
    if target_chapter is None:
        target_chapter = notes[0].chapter if (notes and notes[0].chapter is not None) else 1
    
    print(f"DEBUG: Processing consensus for Subject {payload.subject_id}, Chapter {target_chapter}")

    # 2. Combine note contents for the agent
    combined_notes = "\n---\n".join([f"Note from {n.owner.pseudo_name} ({n.owner.teacher}, {n.owner.year}):\n{n.content}" for n in notes])

    # 3. Call consensus agent...
    try:
        agent = get_consensus_agent()
        if not agent:
            print("ERROR: Consensus agent not configured (check GOOGLE_API_KEY)")
            raise HTTPException(status_code=503, detail="Consensus agent not configured")

        prompt = f"Here are several student notes for Chapter {target_chapter}. Please synthesize them into a single Master Note:\n\n{combined_notes}"
        print(f"DEBUG: Running consensus agent for Chapter {target_chapter} with {len(notes)} notes...")
        print(f"DEBUG: Combined notes length: {len(combined_notes)} characters")
        result = await agent.run(prompt)
        
        consensus_content = str(result.output)
        print("DEBUG: Consensus synthesis complete.")
    except Exception as e:
        print(f"ERROR: Exception during consensus agent run: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI Agent error: {str(e)}")

    # 4. Save/Update MasterNote (Per User, Subject, and Chapter)
    try:
        existing_master = db.query(MasterNote).filter(
            MasterNote.user_id == user_id,
            MasterNote.subject_id == payload.subject_id, 
            MasterNote.chapter == target_chapter
        ).first()
        
        subject = db.query(Subject).filter(Subject.id == payload.subject_id).first()
        topic_name = f"{subject.name if subject else 'Unknown'} - Chapter {target_chapter}"

        if existing_master:
            print(f"DEBUG: Updating existing MasterNote ID {existing_master.id}")
            existing_master.content = consensus_content
            existing_master.version += 1
            db.commit()
        else:
            print(f"DEBUG: Creating new MasterNote for user {user_id}, subject {payload.subject_id}, chapter {target_chapter}")
            new_master = MasterNote(
                user_id=user_id,
                topic=topic_name,
                subject_id=payload.subject_id,
                chapter=target_chapter,
                content=consensus_content,
                version=1
            )
            db.add(new_master)
            db.commit()
    except Exception as e:
        print(f"ERROR: Database error during MasterNote save: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error saving Master Note")

    return {"message": "Consensus reached and Master Note updated", "notes_processed": len(notes), "chapter": target_chapter}

from fastapi.responses import JSONResponse, Response
from io import BytesIO

@router.get("/master/{subject_id}/{chapter}/pdf")
async def download_master_pdf(
    subject_id: int, 
    chapter: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    master = db.query(MasterNote).filter(
        MasterNote.user_id == user_id,
        MasterNote.subject_id == subject_id, 
        MasterNote.chapter == chapter
    ).first()
    
    if not master:
        raise HTTPException(status_code=404, detail="Master Note not found")
    
    # Import reportlab lazily so the app can run without it installed
    try:
        from reportlab.lib.pagesizes import LETTER
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    except Exception:
        return JSONResponse(status_code=503, content={"detail": "PDF generation not available - install 'reportlab' to enable this endpoint."})

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph(f"Master Note: {master.topic}", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Version: {master.version} | Date: {master.created_at.strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Spacer(1, 24))

    # Process content paragraphs
    for p in master.content.split('\n'):
        if p.strip():
            elements.append(Paragraph(p, styles['Normal']))
            elements.append(Spacer(1, 6))

    doc.build(elements)
    pdf_value = buffer.getvalue()
    buffer.close()

    filename = f"MasterNote_{subject_id}_Ch{chapter}.pdf"
    return Response(content=pdf_value, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={filename}"})

@router.get("/master/latest")
async def get_latest_master_note(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    master = db.query(MasterNote).filter(
        MasterNote.user_id == user_id
    ).order_by(MasterNote.created_at.desc()).first()
    
    if not master:
        raise HTTPException(status_code=404, detail="No Master Note found")
    return master

@router.get("/master/{subject_id}/{chapter}")
async def get_master_note(
    subject_id: int, 
    chapter: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    master = db.query(MasterNote).filter(
        MasterNote.user_id == user_id,
        MasterNote.subject_id == subject_id, 
        MasterNote.chapter == chapter
    ).first()
    
    if not master:
        raise HTTPException(status_code=404, detail="Master Note not found for this chapter")
    return master
