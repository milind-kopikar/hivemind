from fastapi import APIRouter
from ..core.ai_agents import GOOGLE_API_KEY, get_ingestion_agent, get_consensus_agent, get_genai_client

router = APIRouter()

@router.get("/health")
def ai_health():
    """Return basic health info about AI integrations (no generation calls made).
    This checks whether GOOGLE_API_KEY is present and whether agent initialization succeeds.
    """
    key_present = bool(GOOGLE_API_KEY)
    ingestion_available = False
    consensus_available = False
    client_ok = False

    try:
        client = get_genai_client()
        client_ok = client is not None
    except Exception as e:
        client_ok = False

    try:
        ingestion_available = get_ingestion_agent() is not None
    except Exception:
        ingestion_available = False

    try:
        consensus_available = get_consensus_agent() is not None
    except Exception:
        consensus_available = False

    return {
        "google_api_key_present": key_present,
        "genai_client_initialized": client_ok,
        "ingestion_agent_available": ingestion_available,
        "consensus_agent_available": consensus_available,
    }
