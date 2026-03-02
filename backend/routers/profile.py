from fastapi import APIRouter, Depends, HTTPException
from models import StandardResponse
from dependencies import verify_session, supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["User Profile & Data Privacy"])

@router.delete("/data", response_model=StandardResponse)
async def delete_user_data(user=Depends(verify_session)):
    """
    Compliance Endpoint: Allows a user to completely delete their chat history and associated medical images.
    Adheres to minimal data retention policies.
    """
    try:
        # 1. Fetch user's chat messages that have images
        messages_resp = supabase.table("chat_messages").select("image_url").eq("user_id", user.id).not_.is_("image_url", "null").execute()
        
        # 2. Extract relative paths from the public URLs and delete from Storage
        # Since images are stored as {user_id}/{uuid}.{ext}, we can just list and delete the user's folder
        files_resp = supabase.storage.from_("medical_images").list(user.id)
        if files_resp:
            file_paths = [f"{user.id}/{file['name']}" for file in files_resp]
            if file_paths:
                supabase.storage.from_("medical_images").remove(file_paths)

        # 3. Delete records from database (Supabase handles cascading if setup, but we'll do explicit here)
        supabase.table("chat_messages").delete().eq("user_id", user.id).execute()
        supabase.table("chat_sessions").delete().eq("user_id", user.id).execute()
        
        return StandardResponse(
            success=True, 
            message="All personal chat data and medical images have been permanently deleted."
        )
    except Exception as e:
        logger.error(f"Data deletion failed for user {user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to safely delete personal data.")
