from fastapi import APIRouter, Depends
from models import StandardResponse
from dependencies import verify_session
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/verify", response_model=StandardResponse)
async def verify_user(user=Depends(verify_session)):
    """
    Endpoint for frontend to verify if the current user session is valid.
    Expects 'Authorization: Bearer <token>'
    """
    return StandardResponse(
        success=True, 
        message="Session is valid.", 
        data={"user_id": user.id, "email": user.email}
    )
