from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Multimodal Medical AI Chatbot API",
    description="Backend API for Symptom Interpretation and Health Awareness",
    version="1.0.0"
)

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

@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical AI Chatbot API"}
