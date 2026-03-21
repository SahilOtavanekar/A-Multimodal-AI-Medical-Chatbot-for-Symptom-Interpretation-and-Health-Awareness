from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from config import settings
import logging
import socket
import jwt

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
    Middleware function to verify Supabase JWT tokens via digital signature.
    This remains stable even if the database session lookup fails on mobile.
    """
    token = credentials.credentials
    try:
        # Verify the token using the Supabase Service Role Key as the secret
        # Supabase uses the HS256 algorithm by default
        payload = jwt.decode(
            token, 
            supabase_key, 
            algorithms=["HS256"], 
            options={"verify_aud": False} # Required as Supabase uses 'authenticated' role as audience
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload.")
            
        # Return an object that supports .id and .email to match existing code
        class AuthUser:
            def __init__(self, uid, email):
                self.id = uid
                self.email = email
                
        return AuthUser(user_id, payload.get("email"))
        
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=401, detail="Session expired.")
    except Exception as e:
        logger.error(f"Auth verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid session token.")
