"""
Hugging Face VQA Dataset Implementation
"""

from typing import Dict, Optional, Any
import torch
from torch.utils.data import Dataset
from datasets import load_dataset

from ..config import config


class HFVQADataset(Dataset):
    """VQA Dataset loaded from Hugging Face"""

    def __init__(
        self,
        split: str = "train",
        processor: Optional[Any] = None,
        max_samples: Optional[int] = None,
        dataset_name: str = "flaviagiammarino/vqa-rad",
    ):
        """
        Initialize VQA Dataset from Hugging Face

        Args:
            split: Dataset split ('train' or 'test')
            processor: BLIP processor for preprocessing
            max_samples: Maximum number of samples to load (for testing)
            dataset_name: Hugging Face dataset name
        """
        self.split = split
        self.processor = processor
        
        # Load dataset from Hugging Face
        print(f"Loading {dataset_name} dataset from Hugging Face...")
        self.dataset = load_dataset(dataset_name, split=split)
        
        if max_samples is not None:
            self.dataset = self.dataset.select(range(min(max_samples, len(self.dataset))))

        # Create answer vocabulary
        self.answer_to_label = self._create_answer_vocabulary()
        self.label_to_answer = {v: k for k, v in self.answer_to_label.items()}

        print(f"Loaded {len(self.dataset)} samples for {split} split")
        print(f"Answer vocabulary size: {len(self.answer_to_label)}")

    def _create_answer_vocabulary(self) -> Dict[str, int]:
        """Create answer vocabulary from dataset"""
        # Collect all unique answers
        answers = set()
        for sample in self.dataset:
            answer = sample["answer"].strip().lower()
            answers.add(answer)
        
        # Create vocabulary
        answer_to_label = {answer: idx for idx, answer in enumerate(sorted(answers))}
        return answer_to_label

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """Get a single sample"""
        sample = self.dataset[idx]

        # Get image, question, and answer
        image = sample["image"].convert("RGB")
        question = sample["question"]
        answer = sample["answer"].strip().lower()

        # Tokenize answer for generation
        labels = None
        if self.processor is not None:
             # Tokenize answer
            answer_encoding = self.processor.tokenizer(
                text=answer,
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=config.model.max_answer_length,
            )
            labels = answer_encoding["input_ids"].squeeze(0)

        result = {
            "image": image,
            "question": question,
            "answer": answer,
            "labels": labels,  # Tokenized answer
            "question_id": idx,  # Use index as question ID
            "image_id": idx,     # Use index as image ID
        }

        # Process with BLIP processor if available
        if self.processor is not None:
            encoding = self.processor(
                images=image,
                text=question,
                return_tensors="pt",
                padding="max_length",
                truncation=True,
                max_length=config.model.max_text_length,
            )

            # Remove batch dimension
            for key in encoding:
                if isinstance(encoding[key], torch.Tensor):
                    encoding[key] = encoding[key].squeeze(0)

            result["encoding"] = encoding

        return result
