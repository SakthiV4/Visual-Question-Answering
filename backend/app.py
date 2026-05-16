
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from transformers import BlipProcessor, BlipForQuestionAnswering
from PIL import Image
import torch
import io

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

# Configuration
MODEL_PATH = "model"  # Expect model in ./model directory
BASE_MODEL = "sakthi04/vqa-model-finetuned"

print("[INFO] Loading Model...")

# Load from local folder if exists (for custom fine-tuned model)
if os.path.exists(MODEL_PATH) and os.listdir(MODEL_PATH):
    print(f"[INFO] Found local model at {MODEL_PATH}")
    load_path = MODEL_PATH
else:
    print(f"[WARN] Local model not found. Downloading {BASE_MODEL}...")
    load_path = BASE_MODEL

try:
    processor = BlipProcessor.from_pretrained(load_path)
    model = BlipForQuestionAnswering.from_pretrained(load_path)
    
    # Use CPU for Free Tier (or CUDA if available on Pro)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"[INFO] Model loaded on {device}")
except Exception as e:
    print(f"[ERROR] Error loading model: {e}")
    raise e

@app.get("/")
def home():
    return {
        "message": "VQA Accessibility API",
        "status": "running", 
        "model": load_path, 
        "device": device,
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
    try:
        # Validate image
        if not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPEG, PNG, etc.)"
            )

        # Read Image
        contents = await image.read()
        raw_image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # Inference with confidence scores
        inputs = processor(raw_image, question, return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=20,
                output_scores=True,
                return_dict_in_generate=True
            )
            sequences = outputs.sequences
            answer = processor.decode(sequences[0], skip_special_tokens=True)
            
            # approximate confidence
            confidence = 1.0
            if hasattr(outputs, 'scores'):
                probs = [torch.softmax(step_scores, dim=-1).max().item() for step_scores in outputs.scores]
                if probs:
                    confidence = sum(probs) / len(probs)
            
        recommendation = ""
        if confidence < 0.8:
            recommendation = "Please take the photo closer or turn on flash."
            
        return JSONResponse(content={
            "success": True,
            "question": question,
            "answer": answer,
            "confidence": round(confidence, 2),
            "recommendation": recommendation
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e), "success": False})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
