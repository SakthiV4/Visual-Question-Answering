"""
FastAPI Backend for VQA PWA
Serves the BLIP-VQA model for visual question answering
"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import torch
from transformers import BlipForQuestionAnswering, BlipProcessor
import io
import base64
import time
import json

# Initialize FastAPI app
app = FastAPI(title="VQA API for Visually Impaired", version="1.0.0")

# Enable CORS for PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and processor
print("Loading BLIP-VQA model...")
model_name = "Salesforce/blip-vqa-base"
model = BlipForQuestionAnswering.from_pretrained(model_name)
processor = BlipProcessor.from_pretrained(model_name)

# Move to GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
model.eval()
print(f"Model loaded on {device}")

# Load model config
with open("../model_config.json", "r") as f:
    model_config = json.load(f)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "model": model_name,
        "device": device,
        "version": "1.0.0"
    }


@app.get("/config")
async def get_config():
    """Get model configuration"""
    return model_config


@app.post("/vqa")
async def answer_question(
    image: UploadFile = File(...),
    question: str = Form(...)
):
    """
    Visual Question Answering endpoint
    
    Args:
        image: Image file (JPEG, PNG)
        question: Natural language question about the image
    
    Returns:
        JSON with answer, confidence, and processing time
    """
    start_time = time.time()
    
    try:
        # Read and process image
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Process inputs
        inputs = processor(pil_image, question, return_tensors="pt").to(device)
        
        # Generate answer
        with torch.no_grad():
            generated_ids = model.generate(**inputs, max_length=10)
        
        # Decode answer
        answer = processor.decode(generated_ids[0], skip_special_tokens=True)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "answer": answer,
            "confidence": 0.85,  # Placeholder (BLIP doesn't provide confidence scores)
            "processing_time_ms": processing_time,
            "question": question,
            "model": model_name
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/vqa/base64")
async def answer_question_base64(request: dict):
    """
    VQA endpoint accepting base64 encoded image
    
    Args:
        request: JSON with {image: base64_string, question: string}
    
    Returns:
        JSON with answer and metadata
    """
    start_time = time.time()
    
    try:
        # Decode base64 image
        image_data = request["image"]
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]
        
        image_bytes = base64.b64decode(image_data)
        pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        question = request["question"]
        
        # Process inputs
        inputs = processor(pil_image, question, return_tensors="pt").to(device)
        
        # Generate answer
        with torch.no_grad():
            generated_ids = model.generate(**inputs, max_length=10)
        
        # Decode answer
        answer = processor.decode(generated_ids[0], skip_special_tokens=True)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "answer": answer,
            "confidence": 0.85,
            "processing_time_ms": processing_time,
            "question": question,
            "model": model_name
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
