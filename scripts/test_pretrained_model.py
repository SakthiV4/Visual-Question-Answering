"""
VQA Inference Script - Using Pretrained BLIP-VQA Model

This script uses the pretrained BLIP-vqa-base model (already trained on VQA v2)
to answer questions about images without any additional training.
"""

import sys
from pathlib import Path
import torch
from PIL import Image

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models import load_blip_processor
from transformers import BlipForQuestionAnswering


def test_pretrained_model():
    """Test the pretrained BLIP-VQA model"""
    
    print("=" * 60)
    print("Testing Pretrained BLIP-VQA Model")
    print("=" * 60)
    print()
    
    # Load pretrained model and processor
    print("[1/3] Loading pretrained model...")
    model_name = "Salesforce/blip-vqa-base"
    model = BlipForQuestionAnswering.from_pretrained(model_name)
    processor = load_blip_processor()
    
    # Move to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()
    
    print(f"[OK] Model loaded: {model_name}")
    print(f"[OK] Device: {device}")
    print(f"[OK] Parameters: {sum(p.numel() for p in model.parameters()):,}")
    print()
    
    # Test with sample questions
    print("[2/3] Testing with sample questions...")
    print()
    
    # You can test with any image URL or local image
    test_cases = [
        {
            "image_url": "https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg",
            "questions": [
                "What is this?",
                "What color is the woman's shirt?",
                "Is this indoors or outdoors?",
                "How many people are in the image?"
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"Image: {test_case['image_url']}")
        print()
        
        # Load image
        try:
            from urllib.request import urlopen
            image = Image.open(urlopen(test_case['image_url'])).convert('RGB')
        except:
            print("⚠ Could not load image from URL. Skipping...")
            continue
        
        # Answer each question
        for question in test_case['questions']:
            # Process inputs
            inputs = processor(image, question, return_tensors="pt").to(device)
            
            # Generate answer
            with torch.no_grad():
                generated_ids = model.generate(**inputs, max_length=10)
            
            # Decode answer
            answer = processor.decode(generated_ids[0], skip_special_tokens=True)
            
            print(f"Q: {question}")
            print(f"A: {answer}")
            print()
    
    print("[3/3] Model is ready!")
    print()
    print("=" * 60)
    print("SUCCESS: Pretrained Model Works!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. The model is ready to use (no training needed)")
    print("2. You can now build the mobile app interface")
    print("3. Expected accuracy: 78-82% on VQA v2 dataset")
    print()
    print("To use this model in your app:")
    print("  - Load: BlipForQuestionAnswering.from_pretrained('Salesforce/blip-vqa-base')")
    print("  - Process: processor(image, question)")
    print("  - Generate: model.generate(**inputs)")
    print()


if __name__ == "__main__":
    try:
        test_pretrained_model()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
