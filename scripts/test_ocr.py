import os
import base64
import asyncio
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv(dotenv_path="backend/.env")
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in backend/.env")
    sys.exit(1)

# Ensure the environment variable is set for the model
os.environ["GOOGLE_API_KEY"] = api_key

async def test_ocr(image_path):
    if not os.path.exists(image_path):
        print(f"Error: File not found at {image_path}")
        return

    print(f"--- Processing Image: {image_path} ---")
    
    try:
        # Read and encode image to base64
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Initialize Gemini Flash model (best for fast OCR)
        model = GoogleModel('gemini-flash-latest')
        
        # Define the Ingestion Agent
        agent = Agent(
            model,
            system_prompt="You are an expert OCR and Note Synthesis agent. Extract all text from the provided image precisely. Use Markdown to format the output if there are headers, bullet points, or sections.",
        )

        # Run the agent with the image data URI
        # Note: Gemini 1.5 Flash supports multimodal input via data URIs in pydantic-ai
        print("Sending to Gemini...")
        result = await agent.run(
            [
                f"Extract all text from this note image precisely:",
                f"data:image/jpeg;base64,{encoded_string}"
            ]
        )
        
        print("\n=== EXTRACTED TEXT START ===")
        print(result.output)
        print("=== EXTRACTED TEXT END ===\n")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_ocr.py <path_to_image.jpg>")
    else:
        asyncio.run(test_ocr(sys.argv[1]))
