from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase Admin Client gracefully to prevent crash during Render build phase
supabase_url = (settings.supabase_url or "https://mhuhgozelxwgmtvugxsq.supabase.co").strip(' "\'')
supabase_key = (settings.supabase_key or "dummy-key").strip(' "\'')
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
