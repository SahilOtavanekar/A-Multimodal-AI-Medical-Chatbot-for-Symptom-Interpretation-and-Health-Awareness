from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from models import StandardResponse
from dependencies import verify_session, supabase
from ai.multimodal import process_multimodal_input, generate_chat_title
from ai.prompts import MEDICAL_SYSTEM_PROMPT
from ai.safety import check_for_emergency, get_emergency_override_message
from ai.severity import classify_risk_severity
from ai.mcp import fetch_authoritative_guidelines, inject_mcp_context
from limiter import limiter
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat & Multimodal Processing"])

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    image_url: Optional[str] = None

@router.post("/", response_model=StandardResponse)
@limiter.limit("5/minute")
async def process_chat(request: Request, payload: ChatRequest, user=Depends(verify_session)):
    """
    Main endpoint for parsing user symptoms, processing optionally attached images,
    identifying emergencies, querying google-genai, and persisting history.
    """
    try:
        session_id = payload.session_id
        if not session_id:
            # Create a brand new session in Supabase on first message
            # AI generation disabled to conserve strict API Free Quota limits. Use first 35 chars.
            session_title = payload.message[:35] + "..." if len(payload.message) > 35 else payload.message
            session_resp = supabase.table("chat_sessions").insert({
                "user_id": user.id,
                "title": session_title
            }).execute()
            if session_resp.data:
                session_id = session_resp.data[0]['id']
            else:
                 raise RuntimeError("Failed to spawn new session.")

         # 1. Enforce Safety Guardrails Pre-Generation
        is_emergency = check_for_emergency(payload.message)
        severity_label = classify_risk_severity(payload.message, is_emergency)
        
        if is_emergency:
            # Hard override if critical keywords are matched
            final_response = get_emergency_override_message()
            logger.warning(f"Emergency Escalation Triggered for User: {user.id}")
        else:
             # Fetch MCP grounding contexts
             mcp_facts = await fetch_authoritative_guidelines(payload.message)
             
             # Fetch up to 4 past messages for conversation context (if we have a session)
             chat_history = []
             if session_id:
                 try:
                     history_res = supabase.table("chat_messages")\
                         .select("role, content")\
                         .eq("session_id", session_id)\
                         .order("created_at", desc=True)\
                         .limit(4)\
                         .execute()
                     if history_res.data:
                         chat_history = list(reversed(history_res.data))
                 except Exception as e:
                     logger.warning(f"Failed to fetch chat history: {e}")
             
             # Multimodal Context Fusion (Gemini)
             base_prompt = f"{MEDICAL_SYSTEM_PROMPT}\n\nUSER INPUT: {payload.message}"
             prompt_with_mcp = inject_mcp_context(base_prompt, mcp_facts)
             final_response = await process_multimodal_input(
                 text_prompt=prompt_with_mcp, 
                 image_url=payload.image_url,
                 chat_history=chat_history
             )

        # 3. Persist User Prompt to DB
        supabase.table("chat_messages").insert({
            "session_id": session_id,
            "user_id": user.id,
            "role": "user",
            "content": payload.message,
            "image_url": payload.image_url,
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
@limiter.limit("15/minute")
async def get_chat_history(request: Request, session_id: str, user=Depends(verify_session)):
    """
    Fetches the chat history from Supabase for a specific session.
    """
    try:
        response = supabase.table("chat_messages").select("*").eq("session_id", session_id).eq("user_id", user.id).order("created_at").execute()
        return StandardResponse(success=True, data=response.data)
    except Exception as e:
        logger.error(f"Failed to fetch history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history.")

@router.get("/sessions", response_model=StandardResponse)
@limiter.limit("15/minute")
async def get_chat_sessions(request: Request, user=Depends(verify_session)):
    """
    Fetches all chat sessions for the authenticated user, ordered by most recently updated.
    """
    try:
        response = supabase.table("chat_sessions").select("*").eq("user_id", user.id).order("updated_at", desc=True).execute()
        return StandardResponse(success=True, data=response.data)
    except Exception as e:
        logger.error(f"Failed to fetch sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat sessions.")

@router.delete("/all", response_model=StandardResponse)
@limiter.limit("5/minute")
async def delete_all_chat_data(request: Request, user=Depends(verify_session)):
    """
    Deletes all chat sessions, messages, and uploaded images for the authenticated user.
    """
    try:
        # 1. Delete all images from the 'medical_images' bucket
        try:
            # List files in the user's directory
            files = supabase.storage.from_("medical_images").list(path=user.id)
            if files:
                file_paths = [f"{user.id}/{file['name']}" for file in files if file['name'] != '.emptyFolderPlaceholder']
                if file_paths:
                    supabase.storage.from_("medical_images").remove(file_paths)
        except Exception as img_err:
            logger.error(f"Failed to delete user images: {str(img_err)}")
            # Proceed to delete db records even if images fail

        # 2. Delete all chat messages (Foreign key cascade might do this, but being explicit is safe)
        supabase.table("chat_messages").delete().eq("user_id", user.id).execute()
        
        # 3. Delete all chat sessions
        supabase.table("chat_sessions").delete().eq("user_id", user.id).execute()

        return StandardResponse(success=True, message="All chat history and data successfully deleted.")
    except Exception as e:
        logger.error(f"Failed to delete chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete chat data.")
