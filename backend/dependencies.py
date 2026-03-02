from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase Admin Client gracefully to prevent crash during Render build phase
supabase_url = settings.supabase_url or "https://mhuhgozelxwgmtvugxsq.supabase.co"
supabase_key = settings.supabase_key or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1odWhnb3plbHh3Z210dnVneHNxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjQ0ODEyMSwiZXhwIjoyMDg4MDI0MTIxfQ.5xRq-lJkj-LYYWrp17hbw3mi6cS-AmyjiBQz6EI83Bc"
supabase: Client = create_client(supabase_url, supabase_key)

security = HTTPBearer()

def verify_session(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Middleware function to verify Supabase JWT tokens via the Authorization header.
    Returns the user data if valid, raises 401 Unauthorized if invalid.
    """
    token = credentials.credentials
    try:
        # Supabase provides getUser() which automatically verifies the JWT validity.
        response = supabase.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Invalid session token.")
        return response.user
    except Exception as e:
        logger.error(f"Auth derivation failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired session token.")
