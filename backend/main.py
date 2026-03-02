from fastapi import FastAPI

app = FastAPI(
    title="Multimodal Medical AI Chatbot API",
    description="Backend API for Symptom Interpretation and Health Awareness",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical AI Chatbot API"}
