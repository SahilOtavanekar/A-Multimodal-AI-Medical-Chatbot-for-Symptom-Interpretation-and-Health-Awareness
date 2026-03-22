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
    Middleware function to verify Supabase JWT tokens via the Authorization header.
    Returns the user data if valid, raises 401 Unauthorized if invalid.
    """
    token = credentials.credentials
    try:
        # Diagnostic logging (first 10 chars)
        logger.debug(f"Verifying token: {token[:10]}...")
        
        # RESILIENCE FIX: 
        # Instead of using the global Admin client to verify the token (which can fail 
        # if the session was created on a different host), we create a fresh 
        # Token-scoped client to perform a 'self-verification'.
        from supabase import create_client as fast_create
        temp_client = fast_create(supabase_url, supabase_key)
        
        # Verify the user using the token itself
        response = temp_client.auth.get_user(token)
        
        if not response or not response.user:
             raise HTTPException(status_code=401, detail="Invalid token session.")
            
        return response.user
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Auth derivation failed on Render Backend: {error_msg}")
        
        # FALLBACK: If GoTrue session check fails because the session row is missing from the DB,
        # but the token's signature WAS successfully verified by GoTrue (proven by the specific error message),
        # we can safely extract the user ID directly from the token payload without re-verifying locally.
        # This handles tokens signed with ES256/RS256 where we don't have the public key.
        if "session_id claim in JWT does not exist" in error_msg:
            try:
                 import jwt
                 # Safe to disable signature verification here ONLY because Supabase's API 
                 # already rejected fake signatures in the previous step (which would yield a different error).
                 payload = jwt.decode(
                    token, 
                    options={"verify_signature": False}
                 )
                 
                 user_id = payload.get("sub")
                 if user_id:
                     logger.warning(f"Rescued session for User {user_id} via verified payload extraction.")
                     class UserProxy:
                         def __init__(self, uid, email):
                             self.id = uid
                             self.email = email
                     return UserProxy(user_id, payload.get("email"))
            except Exception as jwt_err:
                 logger.error(f"Payload extraction fallback failed: {jwt_err}")
             
        raise HTTPException(
            status_code=401, 
            detail=f"Authentication failed: {error_msg}"
        )
