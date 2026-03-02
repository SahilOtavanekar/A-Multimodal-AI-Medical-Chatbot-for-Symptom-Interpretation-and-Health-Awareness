from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from models import StandardResponse
from dependencies import verify_session, supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat & Multimodal Processing"])

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    image_url: Optional[str] = None

@router.post("/", response_model=StandardResponse)
async def process_chat(request: ChatRequest, user=Depends(verify_session)):
    """
    Main endpoint for parsing user symptoms, processing optionally attached images,
    and returning verified health awareness information.
    """
    try:
        # Placeholder logic for Phase 6. Actual Gemini integration happens in Phase 7.
        response_text = f"Received your message: '{request.message}'. Your user ID is verified as {user.id}. AI integration is pending Phase 7."

        # Return standardized response
        return StandardResponse(
            success=True,
            data={
                "response": response_text,
                "session_id": request.session_id or "new_session_id_placeholder",
                "severity": "Low" # Placeholder default
            }
        )
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process chat request.")

@router.get("/history", response_model=StandardResponse)
async def get_chat_history(session_id: str, user=Depends(verify_session)):
    """
    Fetches the chat history from Supabase for a specific session.
    """
    try:
        response = supabase.table("chat_messages").select("*").eq("session_id", session_id).eq("user_id", user.id).order("created_at").execute()
        return StandardResponse(success=True, data=response.data)
    except Exception as e:
        logger.error(f"Failed to fetch history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history.")
