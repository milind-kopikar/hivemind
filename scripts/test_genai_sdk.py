import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="backend/.env")
api_key = os.getenv("GOOGLE_API_KEY")

def run_ocr():
    try:
        image_path = r"C:\Users\Milind Kopikare\Code\hivemind\notes\bio_notes1.jpg"
        if not os.path.exists(image_path):
            print(f"Error: File not found at {image_path}")
            return

        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        client = genai.Client(api_key=api_key)
        
        # User requested gemini-3-flash-preview
        # If this model is not available in their region/tier, we might need gemini-2.0-flash
        model_id = 'gemini-2.0-flash' 
        
        print(f"--- Processing image using google-genai SDK: {image_path} ---")
        
        response = client.models.generate_content(
            model=model_id,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                'Extract all the text in this image verbatim. Do not summarize. If there is a table, format it as a markdown table.'
            ]
        )

        print(f"--- Extracted Text ---")
        print(response.text)
        
    except Exception as e:
        print(f"--- Error occurred ---")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_ocr()
