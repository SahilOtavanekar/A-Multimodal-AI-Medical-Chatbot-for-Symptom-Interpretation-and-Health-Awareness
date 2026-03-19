from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from models import StandardResponse
import logging
from routers import auth, chat, upload, profile
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from limiter import limiter
from audit import AuditLoggingMiddleware

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multimodal Medical AI Chatbot API",
    description="Backend API for Symptom Interpretation and Health Awareness",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register Audit Middleware
app.add_middleware(AuditLoggingMiddleware)

# Configure CORS policies between frontend and backend
# We read FRONTEND_URL from environment variables, defaulting to localhost for dev
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
    "https://your-production-app.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the modular routers
# On Vercel, requests are routed via /api, so we add it as a prefix
prefix = "/api" if os.getenv("VERCEL") else ""

app.include_router(auth.router, prefix=prefix)
app.include_router(chat.router, prefix=prefix)
app.include_router(upload.router, prefix=prefix)
app.include_router(profile.router, prefix=prefix)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Error: {exc.detail} on {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content=StandardResponse(success=False, error=str(exc.detail)).model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)} on {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=StandardResponse(
            success=False, 
            error="Internal Server Error", 
            message="An unexpected error occurred. Please try again later."
        ).model_dump()
    )

@app.get("/", response_model=StandardResponse)
def read_root():
    return StandardResponse(success=True, message="Welcome to the Medical AI Chatbot API")
