from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .database import engine, Base
from .api import auth, ingestion, consensus, rag, analytics
from .api import subjects, notes

# Try to create tables (if pgvector isn't available, this should work with JSON fallback embeddings)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    # Log the error for visibility but continue. Table creation may have partial failures if extensions are missing.
    print(f"Warning: creating tables failed with error: {e}")

app = FastAPI(title="HiveMind API")

# Small startup info and request logging to help Railway debugging
import logging
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(level=logging.INFO)
port = os.getenv("PORT", "8000")
print(f"Starting HiveMind API on port {port}")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"REQ {request.method} {request.url.path} headers={dict(request.headers)}")
        response = await call_next(request)
        print(f"RESP {request.method} {request.url.path} status={response.status_code}")
        return response

app.add_middleware(RequestLoggingMiddleware)

# Configure CORS for mobile and web
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to HiveMind API"}

@app.get("/health")
async def health():
    return {"status": "ok", "port": port}

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
app.include_router(consensus.router, prefix="/consensus", tags=["consensus"])
app.include_router(rag.router, prefix="/rag", tags=["rag"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])

# Simple protected endpoint to verify tokens
from .core.security import decode_access_token
from fastapi import Depends, HTTPException, status, Header

@app.get("/me")
async def read_me(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    scheme, _, token = authorization.partition(" ")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"user": payload}
