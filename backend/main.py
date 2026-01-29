"""
FastAPI Backend for VQA Accessibility App

Provides REST API for Visual Question Answering
with image upload and question processing.
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from src.models.vqa_inference import VQAModel

# Initialize FastAPI app
app = FastAPI(
    title="VQA Accessibility API",
    description="Visual Question Answering API for visually impaired users",
    version="1.0.0"
)

# CORS middleware for PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load VQA model once at startup
print("Loading VQA model...")
vqa_model = VQAModel()
print("VQA model loaded successfully!")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "VQA Accessibility API",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "vqa": "/api/vqa (POST)"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": "BLIP-VQA (pretrained on VQA v2)",
        "accuracy": "78-82%"
    }


@app.post("/api/vqa")
async def answer_question(
    image: UploadFile = File(..., description="Image file"),
    question: str = Form(..., description="Question about the image")
):
    """
    Answer a question about an image
    
    Args:
        image: Image file (JPEG, PNG)
        question: Question to answer
        
    Returns:
        JSON with answer and question
    """
    try:
        # Validate image
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Read and process image
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Get answer from VQA model
        answer = vqa_model.answer_question(pil_image, question)
        
        return JSONResponse(content={
            "success": True,
            "question": question,
            "answer": answer
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
