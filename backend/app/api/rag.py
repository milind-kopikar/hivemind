from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import MasterNote
from ..schemas.schemas import TutorRequest
from ..core.ai_agents import get_model
from ..core.security import decode_access_token
from pydantic_ai import Agent
from typing import Optional
import json
import re

router = APIRouter()

# In-memory store for the latest quiz per user (dev-only; replace with persistent store for production)
last_quiz_by_user: dict[int, dict] = {}

@router.post("/tutor")
async def tutor_interaction(
    payload: TutorRequest, 
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
):
    user_id = None
    if authorization:
        scheme, _, token = authorization.partition(" ")
        token_data = decode_access_token(token)
        if token_data:
            from ..models import User
            user = db.query(User).filter(User.email == token_data.get('sub')).first()
            if user:
                user_id = user.id

    master = None
    if user_id:
        if payload.subject_id > 0 and payload.chapter > 0:
            master = db.query(MasterNote).filter(
                MasterNote.user_id == user_id,
                MasterNote.subject_id == payload.subject_id, 
                MasterNote.chapter == payload.chapter
            ).first()
        
        # Fallback: find the most recently updated master note for this user
        if not master:
            master = db.query(MasterNote).filter(
                MasterNote.user_id == user_id
            ).order_by(MasterNote.created_at.desc()).first()

    context = ""
    if master:
        context = f"Here is the collective knowledge (Master Note) for this chapter created by the student:\n\n{master.content}\n\n"
    else:
        context = "Note: No specific Master Note has been found for the requested Subject/Chapter. Use your general training data to help the student.\n\n"

    # 2. Setup Tutor Agent
    model = get_model('gemini-pro-latest')
    tutor_agent = Agent(
        model,
        system_prompt=(
            "You are an expert AI Tutor. Your goal is to help students learn using the collective classroom knowledge (Master Note provided). "
            f"Mode: {payload.mode}. "
            "If in 'chat' mode, answer questions clearly and directly using the Master Note as context when available. "
            "If in 'quiz' mode, respond as follows: "
            "- When the student asks for a quiz (e.g., 'quiz me', 'give me a question'), produce exactly ONE multiple-choice question with four options labeled A), B), C), and D). "
            "- Do NOT include or reveal the correct answer in the same response — wait for the student to submit their choice. "
            "- When the student submits an answer (e.g., 'I choose C' or 'Answer: B'), evaluate that choice against the Master Note and reply 'Correct' or 'Incorrect' followed by a brief explanation referencing the Master Note. "
            "If in 'flashcards' mode, provide a term and its definition. "
            "Always be encouraging, concise, and academic."
        )
    )

    # 3. Special handling for quiz mode to keep state and evaluate answers
    if payload.mode == 'quiz':
        if not user_id:
            return {"answer": "Please login to use Quiz mode."}

        user_input = payload.question.strip()
        normalized = user_input.lower()

        # Detect answer submissions like 'A', 'I choose B', 'Answer: C', etc.
        if re.search(r"\b([abcd])\b", normalized):
            # This is an answer submission
            if user_id not in last_quiz_by_user:
                return {"answer": "I don't have an active quiz question for you. Say 'Quiz me' to get a question."}
            match = re.search(r"([abcd])", normalized)
            choice = match.group(1).upper() if match else None
            quiz = last_quiz_by_user.get(user_id, {})
            correct = quiz.get('answer')
            explanation = quiz.get('explanation', '')
            if not choice or not correct:
                return {"answer": "I couldn't parse your answer—please reply with A, B, C, or D."}
            if choice == correct:
                return {"answer": f"Correct. {explanation}"}
            else:
                return {"answer": f"Incorrect. The correct answer is {correct}. {explanation}"}

        # Otherwise, treat as a request for a new quiz question
        try:
            prompt = (
                f"{context}Please generate exactly ONE multiple-choice question based on the above Master Note. "
                "Respond ONLY with a valid JSON object with these fields: \n"
                "{\"question\": \"...\", \"options\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"}, \"answer\": \"A\", \"explanation\": \"...\"}\n"
                "Do NOT include any extra text outside the JSON. The field 'answer' should contain the correct label (A/B/C/D)."
            )
            result = await tutor_agent.run(prompt)
            out = str(result.output).strip()

            # Try to extract JSON substring if agent adds surrounding text
            m = re.search(r"(\{.*\})", out, re.S)
            json_str = m.group(1) if m else out
            parsed = json.loads(json_str)

            # Store the quiz (including answer) server-side for later evaluation
            last_quiz_by_user[user_id] = parsed

            # Build user-facing question without revealing the answer
            options_text = "\n".join([f"{k}) {v}" for k, v in parsed['options'].items()])
            return {"answer": f"{parsed['question']}\n\n{options_text}"}
        except Exception as e:
            print(f"Quiz generation error: {e}")
            return {"answer": "Sorry, I couldn't generate a quiz right now. Try again in a moment."}

    # 4. Regular chat or flashcards handling
    try:
        prompt = f"{context}Student Request: {payload.question}"
        result = await tutor_agent.run(prompt)
        return {"answer": str(result.output)}
    except Exception as e:
        print(f"Tutor Error: {e}")
        return {"answer": "I'm sorry, I am having trouble connecting to the brain right now."}


@router.get("/search")
async def search_rag():
    return {"message": "RAG search results"}

@router.get("/quiz/latest")
async def get_latest_quiz(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    scheme, _, token = authorization.partition(" ")
    token_data = decode_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Find user id
    from ..models import User
    user = db.query(User).filter(User.email == token_data.get('sub')).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    quiz = last_quiz_by_user.get(user.id)
    if not quiz:
        raise HTTPException(status_code=404, detail="No active quiz found")
    # Remove the answer before returning
    sanitized = {"question": quiz['question'], "options": quiz['options']}
    return sanitized
