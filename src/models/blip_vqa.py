"""
BLIP VQA Model Implementation
"""

from typing import Optional
import torch.nn as nn
from transformers import BlipForQuestionAnswering, BlipProcessor

from ..config import config


class BLIPVQAModel(nn.Module):
    """BLIP-based VQA Model"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        num_labels: Optional[int] = None,
        from_pretrained: bool = True,
    ):
        """
        Initialize BLIP VQA Model

        Args:
            model_name: Hugging Face model name
            num_labels: Number of answer classes
            from_pretrained: Whether to load pretrained weights
        """
        super().__init__()

        if model_name is None:
            model_name = config.model.model_name

        self.model_name = model_name
        self.num_labels = num_labels

        # Load pretrained model
        if from_pretrained:
            print(f"Loading pretrained model: {model_name}")
            self.model = BlipForQuestionAnswering.from_pretrained(model_name)

        # Classifier adjustment removed for generative VQA

    def forward(
        self,
        pixel_values,
        input_ids,
        attention_mask=None,
        labels=None,
        return_dict=True,
    ):
        """
        Forward pass

        Args:
            pixel_values: Image tensors
            input_ids: Question token IDs
            attention_mask: Attention mask for questions
            labels: Answer labels (for training)
            return_dict: Whether to return dict

        Returns:
            Model outputs
        """
        outputs = self.model(
            pixel_values=pixel_values,
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
            return_dict=return_dict,
        )
        return outputs

    def generate(
        self, pixel_values, input_ids, attention_mask=None, max_length=10, num_beams=3
    ):
        """
        Generate answer text

        Args:
            pixel_values: Image tensors
            input_ids: Question token IDs
            attention_mask: Attention mask
            max_length: Maximum answer length
            num_beams: Number of beams for beam search

        Returns:
            Generated answer token IDs
        """
        outputs = self.model.generate(
            pixel_values=pixel_values,
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=max_length,
            num_beams=num_beams,
        )
        return outputs

    def save_pretrained(self, save_directory: str):
        """Save model to directory"""
        self.model.save_pretrained(save_directory)
        print(f"Model saved to {save_directory}")

    def get_model_info(self):
        """Get model architecture information"""
        return {
            "model_name": self.model_name,
            "num_labels": self.num_labels,
            "vision_encoder": config.model.vision_encoder,
            "text_encoder": config.model.text_encoder,
            "hidden_size": config.model.hidden_size,
            "num_attention_heads": config.model.num_attention_heads,
        }


def load_blip_model(num_labels: int):
    """
    Load BLIP VQA model

    Args:
        num_labels: Number of answer classes

    Returns:
        BLIPVQAModel instance
    """
    model = BLIPVQAModel(
        model_name=config.model.model_name, num_labels=num_labels, from_pretrained=True
    )
    return model


def load_blip_processor():
    """
    Load BLIP processor

    Returns:
        BlipProcessor instance
    """
    print(f"Loading processor: {config.model.model_name}")
    processor = BlipProcessor.from_pretrained(config.model.model_name)
    return processor
