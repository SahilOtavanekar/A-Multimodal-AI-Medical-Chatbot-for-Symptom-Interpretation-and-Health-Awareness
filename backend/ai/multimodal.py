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

async def process_multimodal_input(text_prompt: str, image_url: str = None, chat_history: list = None) -> str:
    """
    Core Context Fusion module using Gemini.
    Takes user symptoms (text) and optional medical images, and asks Gemini.
    """
    if not client:
        raise RuntimeError("Gemini AI Client is not initialized due to missing API keys.")

    contents = []

    # 1. Format previous conversation history as a string prefix
    history_context = ""
    if chat_history:
        history_context += "--- PREVIOUS CONVERSATION CONTEXT ---\n"
        for msg in chat_history:
            role = "USER" if msg['role'] == "user" else "ASSISTANT"
            content_text = str(msg.get('content', ''))
            if content_text.strip():
                history_context += f"{role}: {content_text}\n\n"
        history_context += "--- END CONTEXT, RESUMING CURRENT TURN ---\n\n"

    # Append the formatted history to the current text prompt
    final_text_prompt = history_context + text_prompt

    # 2. Build the current turn's content
    current_parts = []
    
    # If image URL exists, fetch it and append as a Part to the current turn
    if image_url:
        try:
            b64_image = await download_image_as_base64(image_url)
            # Determine mime type naively from URL extension or default to jpeg
            mime_type = "image/jpeg"
            if image_url.lower().endswith(".png"):
                mime_type = "image/png"
            elif image_url.lower().endswith(".webp"):
                mime_type = "image/webp"

            current_parts.append(
                types.Part.from_bytes(
                    data=base64.b64decode(b64_image),
                    mime_type=mime_type
                )
            )
        except Exception as e:
            logger.error(f"Failed to fetch or process image for AI: {e}")
            raise RuntimeError("Failed to process the uploaded image for AI reasoning.")

    # Always append the user's combined text prompt
    current_parts.append(types.Part.from_text(text=final_text_prompt))
    
    # Add the current turn to the overall contents payload as a user message
    contents.append(
        types.Content(
            role="user",
            parts=current_parts
        )
    )

    try:
        # Use gemini-2.5-flash as the fast multimodal general model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.2, # Low temperature for more deterministic, factual responses
            )
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Gemini API Error: {error_msg}")
        raise RuntimeError(f"AI processing service error: {error_msg}")

async def generate_chat_title(first_message: str) -> str:
    """Generates a concise 3-4 word title for a new chat session based on the first message."""
    if not client:
        return f"Session: {first_message[:15]}..."
        
    try:
        prompt = f"Summarize the following medical query into a very concise, descriptive title (maximum 4 words, no quotes, no period): {first_message}"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
            )
        )
        title = response.text.strip().replace('"', '').replace('.', '')
        return title if len(title) > 0 else f"Session: {first_message[:15]}..."
    except Exception as e:
        logger.error(f"Failed to generate title: {e}")
        return f"Session: {first_message[:15]}..."
