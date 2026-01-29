"""
VQA Inference API - Production Ready

This module provides a simple API for Visual Question Answering
using the pretrained BLIP-VQA model (trained on VQA v2).

Accuracy: 78-82% on VQA v2
No training required - ready for production!
"""

import torch
from PIL import Image
from transformers import BlipProcessor, BlipForQuestionAnswering
from typing import Union
import io

class VQAModel:
    """
    Visual Question Answering Model
    
    Uses pretrained BLIP-VQA model (Salesforce/blip-vqa-base)
    trained on VQA v2 dataset with 78-82% accuracy.
    """
    
    def __init__(self, device: str = None):
        """
        Initialize VQA model
        
        Args:
            device: 'cuda' or 'cpu'. If None, auto-detects GPU.
        """
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        print(f"Loading VQA model on {self.device}...")
        
        # Load pretrained model
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
        self.model = BlipForQuestionAnswering.from_pretrained(
            "Salesforce/blip-vqa-base"
        ).to(self.device)
        
        print("Model loaded successfully!")
    
    def answer_question(
        self, 
        image: Union[Image.Image, str, bytes], 
        question: str,
        max_length: int = 20
    ) -> str:
        """
        Answer a question about an image
        
        Args:
            image: PIL Image, file path, or image bytes
            question: Question to answer
            max_length: Maximum length of answer
            
        Returns:
            Answer string
        """
        # Load image if needed
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, bytes):
            image = Image.open(io.BytesIO(image)).convert('RGB')
        elif not isinstance(image, Image.Image):
            raise ValueError("Image must be PIL Image, file path, or bytes")
        
        # Process inputs
        inputs = self.processor(image, question, return_tensors="pt").to(self.device)
        
        # Generate answer
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_length=max_length)
        
        # Decode answer
        answer = self.processor.decode(outputs[0], skip_special_tokens=True)
        
        return answer
    
    def batch_answer(
        self, 
        images: list, 
        questions: list,
        max_length: int = 20
    ) -> list:
        """
        Answer multiple questions about multiple images
        
        Args:
            images: List of PIL Images, file paths, or image bytes
            questions: List of questions (same length as images)
            max_length: Maximum length of answers
            
        Returns:
            List of answer strings
        """
        if len(images) != len(questions):
            raise ValueError("Number of images must match number of questions")
        
        answers = []
        for image, question in zip(images, questions):
            answer = self.answer_question(image, question, max_length)
            answers.append(answer)
        
        return answers


# Example usage
if __name__ == "__main__":
    # Initialize model
    vqa = VQAModel()
    
    # Example 1: Answer question about an image
    from PIL import Image
    import requests
    from io import BytesIO
    
    # Load sample image
    url = "https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg"
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    
    # Ask questions
    questions = [
        "What is the woman doing?",
        "What color is her shirt?",
        "Is she on a beach?",
        "How many people are in the image?"
    ]
    
    print("\nVQA Demo:")
    print("="*60)
    for question in questions:
        answer = vqa.answer_question(image, question)
        print(f"Q: {question}")
        print(f"A: {answer}\n")
