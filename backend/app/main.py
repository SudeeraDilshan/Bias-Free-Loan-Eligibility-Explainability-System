"""
FastAPI Backend for Loan Eligibility Prediction System
Handles predictions, SHAP explanations, and detailed reasoning reports
"""
import torch  # Fix for WinError 1114 DLL load failed (OpenMP conflict)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add project paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.append(base_dir)

# Ensure UTF-8 output encoding to prevent Windows cp1252 print crashes
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from app.services.model_manager import model_manager
from app.services.llm_explainer import llm_explainer
from app.routes.health import router as health_router
from app.routes.predictions import router as predictions_router
from app.routes.extractions import router as extractions_router

# Initialize FastAPI app
app = FastAPI(
    title="Bias-Free Loan Eligibility System",
    description="AI-powered loan prediction with explainability and fairness analysis",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(predictions_router, tags=["Predictions"])
app.include_router(extractions_router, tags=["Document Extraction"])

@app.on_event("startup")
async def startup_event():
    model_manager.load_models()
    llm_explainer.load_model()

if __name__ == "__main__":
    # Load models on startup
    model_manager.load_models()
    llm_explainer.load_model()
    
    # Run server
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
