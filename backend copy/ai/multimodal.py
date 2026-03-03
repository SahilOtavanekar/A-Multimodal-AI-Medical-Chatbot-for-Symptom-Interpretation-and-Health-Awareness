import logging
from google import genai
from google.genai import types
from config import settings
import httpx
import base64

logger = logging.getLogger(__name__)

# Initialize the new Google GenAI SDK client
try:
    client = genai.Client(api_key=settings.gemini_api_key)
except Exception as e:
    logger.error(f"Failed to initialize Gemini Client: {e}")
    client = None

async def download_image_as_base64(image_url: str) -> str:
    """Helper to download image from Supabase public URL and convert to Base64 for Gemini"""
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

async def process_multimodal_input(text_prompt: str, image_url: str = None) -> str:
    """
    Core Context Fusion module using Gemini.
    Takes user symptoms (text) and optional medical images, and asks Gemini.
    """
    if not client:
        raise RuntimeError("Gemini AI Client is not initialized due to missing API keys.")

    contents = []

    # If image URL exists, fetch it and append as a Part to the contents list
    if image_url:
        try:
            b64_image = await download_image_as_base64(image_url)
            # Determine mime type naively from URL extension or default to jpeg
            mime_type = "image/jpeg"
            if image_url.lower().endswith(".png"):
                mime_type = "image/png"
            elif image_url.lower().endswith(".webp"):
                mime_type = "image/webp"

            contents.append(
                types.Part.from_bytes(
                    data=base64.b64decode(b64_image),
                    mime_type=mime_type
                )
            )
        except Exception as e:
            logger.error(f"Failed to fetch or process image for AI: {e}")
            raise RuntimeError("Failed to process the uploaded image for AI reasoning.")

    # Always append the user's text symptom description
    contents.append(
        types.Part.from_text(text=text_prompt)
    )

    try:
        # Use gemini-2.5-flash natively utilizing ASYNC client to prevent blocking fastAPI
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.2, # Low temperature for more deterministic, factual responses
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        raise RuntimeError(f"AI processing service is currently unavailable. Ensure GEMINI_API_KEY is correct. Detail: {e}")
