import logging
import httpx
import base64
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)

# Initialize the OpenAI client
try:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
except Exception as e:
    logger.error(f"Failed to initialize OpenAI Client: {e}")
    client = None

async def download_image_as_base64(image_url: str) -> str:
    """Helper to download image from Supabase public URL and convert to Base64 for OpenAI"""
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

async def process_multimodal_input(text_prompt: str, image_url: str = None, chat_history: list = None) -> str:
    """
    Core Context Fusion module using OpenAI.
    Takes user symptoms (text) and optional medical images, and asks OpenAI.
    """
    if not client:
        raise RuntimeError("OpenAI Client is not initialized due to missing API keys.")

    messages = []
    
    # Optional: We could set a system message here for medical behavior, but the text_prompt already encapsulates this.
    # We will build messages based on chat_history
    if chat_history:
        for msg in chat_history:
            role = "user" if msg['role'] == "user" else "assistant"
            content_text = str(msg.get('content', ''))
            if content_text.strip():
                messages.append({"role": role, "content": content_text})

    # Build the current turn's content array for multimodal support
    current_content = []
    
    # Always append the user's text prompt (will contain safety wrappers etc)
    current_content.append({"type": "text", "text": text_prompt})

    # If image URL exists, fetch it and append as an image_url to the current turn
    if image_url:
        try:
            b64_image = await download_image_as_base64(image_url)
            mime_type = "image/jpeg"
            if image_url.lower().endswith(".png"):
                mime_type = "image/png"
            elif image_url.lower().endswith(".webp"):
                mime_type = "image/webp"

            # OpenAI expects the base64 string formatted as a data URL
            data_url = f"data:{mime_type};base64,{b64_image}"
            
            current_content.append({
                "type": "image_url",
                "image_url": {
                    "url": data_url
                }
            })
        except Exception as e:
            logger.error(f"Failed to fetch or process image for AI: {e}")
            raise RuntimeError("Failed to process the uploaded image for AI reasoning.")
    
    # Add the current turn to the messages payload
    messages.append({
        "role": "user",
        "content": current_content
    })

    try:
        # Use gpt-4o-mini as the fast, multimodal general model
        response = await client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            temperature=0.2, # Low temperature for more deterministic, factual responses
        )
        return response.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        logger.error(f"OpenAI API Error: {error_msg}")
        raise RuntimeError(f"AI processing service error: {error_msg}")

async def generate_chat_title(first_message: str) -> str:
    """Generates a concise 3-4 word title for a new chat session based on the first message."""
    if not client:
        return f"Session: {first_message[:15]}..."
        
    try:
        prompt = f"Summarize the following medical query into a very concise, descriptive title (maximum 4 words, no quotes, no period): {first_message}"
        response = await client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        title = response.choices[0].message.content.strip().replace('"', '').replace('.', '')
        return title if len(title) > 0 else f"Session: {first_message[:15]}..."
    except Exception as e:
        logger.error(f"Failed to generate title: {e}")
        return f"Session: {first_message[:15]}..."
