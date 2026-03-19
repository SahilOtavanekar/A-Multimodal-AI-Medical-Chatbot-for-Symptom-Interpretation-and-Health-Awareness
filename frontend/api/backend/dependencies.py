from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from config import settings
import logging
import socket

# --- IPv6 / NAT64 Compatibility Patch ---
# Force Python's DNS resolver to prioritize IPv6 addresses (AF_INET6) 
# to bypass local ISP IPv4 blackholes that cause connection timeouts.
_orig_getaddrinfo = socket.getaddrinfo
def _ipv6_first_getaddrinfo(*args, **kwargs):
    res = _orig_getaddrinfo(*args, **kwargs)
    return sorted(res, key=lambda x: x[0] == socket.AF_INET6, reverse=True)
socket.getaddrinfo = _ipv6_first_getaddrinfo
# ----------------------------------------

logger = logging.getLogger(__name__)

# Initialize Supabase Admin Client using environment variables only.
# No hardcoded fallbacks are allowed.
if not settings.supabase_url or not settings.supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be securely set for the backend.")

supabase_url = settings.supabase_url.strip(' "\'')
supabase_key = settings.supabase_key.strip(' "\'')
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
