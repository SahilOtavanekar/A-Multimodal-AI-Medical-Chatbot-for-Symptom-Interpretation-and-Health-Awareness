from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Define a global rate limiter using the client's IP address
# In a distributed production environment, you would configure this to use Redis
limiter = Limiter(key_func=get_remote_address)

def get_user_id_or_ip(request: Request) -> str:
    """
    Custom key function for rate limiting that tries to use the 
    authenticated user's ID, falling back to IP address for public routes.
    """
    # If we had a mechanism to extract user_id globally from request state, we'd use it here.
    # For now, IP address is a safe default fallback.
    return get_remote_address(request)

# You can also define custom key_func for authenticated-only endpoints separately 
# if you need strict per-user limits regardless of IP.
