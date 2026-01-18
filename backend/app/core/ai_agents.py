import os
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Use the API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_genai_client():
    if not GOOGLE_API_KEY:
        return None
    return genai.Client(api_key=GOOGLE_API_KEY)

async def extract_text_from_image(image_bytes: bytes) -> str:
    """Uses the latest google-genai SDK for high-quality OCR."""
    client = get_genai_client()
    if not client:
        raise ValueError("GOOGLE_API_KEY not configured")
    
    # Using gemini-2.0-flash which was very reliable in tests
    model_id = 'gemini-2.0-flash'
    
    response = client.models.generate_content(
        model=model_id,
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg',
            ),
            'Extract all the text in this image verbatim. Do not summarize. Maintain the structure and if there is a table, format it as a markdown table.'
        ]
    )
    return response.text

def get_model(model_name: str):
    """Initializes the Google model. It picks up GOOGLE_API_KEY from os.environ."""
    return GoogleModel(model_name)

# Lazy-initialize agents so the server can run without API keys for local testing
_ingestion_agent = None
_consensus_agent = None

from pydantic_ai.exceptions import UserError

def get_ingestion_agent():
    global _ingestion_agent
    if _ingestion_agent is not None:
        return _ingestion_agent
    if not GOOGLE_API_KEY:
        return None
    try:
        # Using 'gemini-flash-latest' which was confirmed to work in Jan 2026 env
        _ingestion_agent = Agent(
            get_model('gemini-flash-latest'),
            system_prompt="You are an expert OCR and Note Synthesis agent. Convert images of handwritten notes into structured Markdown. Maintain original meaning but organize clearly.",
        )
        return _ingestion_agent
    except Exception as e:
        print(f"Warning: ingestion agent not available: {e}")
        return None

def get_consensus_agent():
    global _consensus_agent
    if _consensus_agent is not None:
        return _consensus_agent
    if not GOOGLE_API_KEY:
        return None
    try:
        # Using 'gemini-pro-latest' which was confirmed to work in Jan 2026 env
        _consensus_agent = Agent(
            get_model('gemini-pro-latest'),
            system_prompt="""You are a Master Note Synthesizer. 
            You will be provided with multiple sets of student notes for the same chapter.
            Your task is to create a single, comprehensive, and high-quality Markdown study guide.
            
            1. Combine all unique facts and concepts into a logical flow.
            2. Highlighting key terminology in bold.
            3. Use clear headings and subheadings.
            4. If there are tables or lists in the source, integrate them cleanly.
            5. Ensure the final result is a "Master Note" that a student could use as their sole study resource.
            6. Do not mention that you are an AI or that you are synthesizing notes. Just provide the note content.""",
        )
        return _consensus_agent
    except Exception as e:
        print(f"Warning: consensus agent not available: {e}")
        return None
