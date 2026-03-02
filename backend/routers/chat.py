from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from models import StandardResponse
from dependencies import verify_session, supabase
from ai.multimodal import process_multimodal_input
from ai.prompts import MEDICAL_SYSTEM_PROMPT
from ai.safety import check_for_emergency, get_emergency_override_message
from ai.severity import classify_risk_severity
import uuid
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
    identifying emergencies, querying google-genai, and persisting history.
    """
    try:
        session_id = request.session_id
        if not session_id:
            # Create a brand new session in Supabase on first message
            session_resp = supabase.table("chat_sessions").insert({
                "user_id": user.id,
                "title": f"Session {request.message[:20]}..."
            }).execute()
            if session_resp.data:
                session_id = session_resp.data[0]['id']
            else:
                 raise RuntimeError("Failed to spawn new session.")

        # 1. Enforce Safety Guardrails Pre-Generation
        is_emergency = check_for_emergency(request.message)
        severity_label = classify_risk_severity(request.message, is_emergency)
        
        if is_emergency:
            # Hard override if critical keywords are matched
            final_response = get_emergency_override_message()
            logger.warning(f"Emergency Escalation Triggered for User: {user.id}")
        else:
             # 2. Multimodal Context Fusion (Gemini)
             prompt = f"{MEDICAL_SYSTEM_PROMPT}\n\nUSER INPUT: {request.message}"
             final_response = await process_multimodal_input(text_prompt=prompt, image_url=request.image_url)

        # 3. Persist User Prompt to DB
        supabase.table("chat_messages").insert({
            "session_id": session_id,
            "user_id": user.id,
            "role": "user",
            "content": request.message,
            "image_url": request.image_url,
            "severity": "N/A" # Prompts don't get severity tags, AI responses do
        }).execute()
        
        # 4. Persist AI Response to DB
        supabase.table("chat_messages").insert({
            "session_id": session_id,
            "user_id": user.id,
            "role": "assistant",
            "content": final_response,
            "image_url": None,
            "severity": severity_label
        }).execute()

        # Return standardized response back to frontend
        return StandardResponse(
            success=True,
            data={
                "response": final_response,
                "session_id": session_id,
                "severity": severity_label
            }
        )
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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
