"""
Data loading utilities
"""

from typing import Optional, Tuple
import torch
from torch.utils.data import DataLoader

from .dataset import VQADataset
from ..config import config


def collate_fn(batch):
    """Custom collate function for VQA dataset"""
    # Separate different components
    images = []
    questions = []
    answers = []
    labels = []
    question_ids = []
    image_ids = []
    encodings = []

    for sample in batch:
        images.append(sample["image"])
        questions.append(sample["question"])
        answers.append(sample["answer"])
        
        if "labels" in sample and sample["labels"] is not None:
            labels.append(sample["labels"])
        elif "answer_label" in sample: # Fallback for old dataset class
             labels.append(torch.tensor(sample["answer_label"]))

        question_ids.append(sample["question_id"])
        image_ids.append(sample["image_id"])

        if "encoding" in sample:
            encodings.append(sample["encoding"])

    # Create batch dictionary
    batch_dict = {
        "images": images,
        "questions": questions,
        "answers": answers,
        "question_ids": question_ids,
        "image_ids": image_ids,
    }

    if labels:
        batch_dict["labels"] = torch.stack(labels)

    # Stack encodings if available
    if encodings:
        batch_encoding = {}
        for key in encodings[0].keys():
            batch_encoding[key] = torch.stack([enc[key] for enc in encodings])
        batch_dict["encoding"] = batch_encoding

    return batch_dict


def create_dataloaders(
    processor,
    train_max_samples: Optional[int] = None,
    val_max_samples: Optional[int] = None,
    batch_size: Optional[int] = None,
    num_workers: Optional[int] = None,
    use_hf_dataset: bool = True,
    dataset_name: str = "flaviagiammarino/vqa-rad",
) -> Tuple[DataLoader, DataLoader]:
    """
    Create train and validation dataloaders

    Args:
        processor: BLIP processor
        train_max_samples: Maximum training samples (for testing)
        val_max_samples: Maximum validation samples (for testing)
        batch_size: Batch size (uses config if None)
        num_workers: Number of workers (uses config if None)
        use_hf_dataset: Whether to use Hugging Face dataset (default: True)
        dataset_name: Hugging Face dataset name

    Returns:
        Tuple of (train_loader, val_loader)
    """
    if batch_size is None:
        batch_size = config.training.batch_size
    if num_workers is None:
        num_workers = config.data.num_workers

    # Create datasets
    if use_hf_dataset:
        from .hf_dataset import HFVQADataset
        
        train_dataset = HFVQADataset(
            split="train", 
            processor=processor, 
            max_samples=train_max_samples,
            dataset_name=dataset_name
        )

        # Use 'test' split for validation (VQA-RAD doesn't have validation split)
        val_dataset = HFVQADataset(
            split="test", 
            processor=processor, 
            max_samples=val_max_samples,
            dataset_name=dataset_name
        )
    else:
        train_dataset = VQADataset(
            split="train", processor=processor, max_samples=train_max_samples
        )

        val_dataset = VQADataset(
            split="validation", processor=processor, max_samples=val_max_samples
        )

    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=config.data.pin_memory,
        collate_fn=collate_fn,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=config.data.pin_memory,
        collate_fn=collate_fn,
    )

    print("Created dataloaders:")
    print(f"  Train: {len(train_dataset)} samples, {len(train_loader)} batches")
    print(f"  Val: {len(val_dataset)} samples, {len(val_loader)} batches")

    return train_loader, val_loader
