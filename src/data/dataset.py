"""
VQA Dataset Implementation
"""

import json
from typing import Dict, List, Optional, Tuple, Any

import torch
from torch.utils.data import Dataset
from PIL import Image

from ..config import config, RAW_DATA_DIR, PROCESSED_DATA_DIR


class VQADataset(Dataset):
    """VQA v2 Dataset"""

    def __init__(
        self,
        split: str = "train",
        processor: Optional[Any] = None,
        transform: Optional[Any] = None,
        max_samples: Optional[int] = None,
    ):
        """
        Initialize VQA Dataset

        Args:
            split: Dataset split ('train' or 'validation')
            processor: BLIP processor for preprocessing
            transform: Optional image transformations
            max_samples: Maximum number of samples to load (for testing)
        """
        self.split = split
        self.processor = processor
        self.transform = transform

        # Load questions and annotations
        self.questions, self.annotations = self._load_data(split)

        if max_samples is not None:
            self.questions = self.questions[:max_samples]
            self.annotations = self.annotations[:max_samples]

        self.image_dir = RAW_DATA_DIR / f"{split}2014"
        self.answer_to_label = self._create_answer_vocabulary()
        self.label_to_answer = {v: k for k, v in self.answer_to_label.items()}

        print(f"Loaded {len(self.questions)} samples for {split} split")
        print(f"Answer vocabulary size: {len(self.answer_to_label)}")

    def _load_data(self, split: str) -> Tuple[List[Dict], List[Dict]]:
        """Load questions and annotations from JSON files"""
        questions_file = (
            RAW_DATA_DIR / f"v2_OpenEnded_mscoco_{split}2014_questions.json"
        )
        annotations_file = RAW_DATA_DIR / f"v2_mscoco_{split}2014_annotations.json"

        # Check if files exist
        if not questions_file.exists():
            raise FileNotFoundError(
                f"Questions file not found: {questions_file}\n"
                f"Please download VQA v2 dataset from https://visualqa.org/download.html"
            )
        if not annotations_file.exists():
            raise FileNotFoundError(
                f"Annotations file not found: {annotations_file}\n"
                f"Please download VQA v2 dataset from https://visualqa.org/download.html"
            )

        with open(questions_file, "r") as f:
            questions_data = json.load(f)
        with open(annotations_file, "r") as f:
            annotations_data = json.load(f)

        return questions_data["questions"], annotations_data["annotations"]

    def _create_answer_vocabulary(self, min_freq: int = 9) -> Dict[str, int]:
        """Create answer vocabulary from training data"""
        vocab_file = PROCESSED_DATA_DIR / "answer_vocab.json"

        # Load existing vocabulary if available
        if vocab_file.exists():
            with open(vocab_file, "r") as f:
                return json.load(f)

        # Create vocabulary from training data
        if self.split == "train":
            answer_counts: Dict[str, int] = {}
            for ann in self.annotations:
                for answer_item in ann["answers"]:
                    answer = answer_item["answer"]
                    answer_counts[answer] = answer_counts.get(answer, 0) + 1

            # Filter answers by minimum frequency
            answer_to_label = {
                answer: idx
                for idx, (answer, count) in enumerate(sorted(answer_counts.items()))
                if count >= min_freq
            }

            # Save vocabulary
            with open(vocab_file, "w") as f:
                json.dump(answer_to_label, f)

            print(f"Created answer vocabulary with {len(answer_to_label)} answers")
            return answer_to_label
        else:
            # For validation, load training vocabulary
            if not vocab_file.exists():
                raise FileNotFoundError(
                    "Answer vocabulary not found. Please run training data loading first."
                )
            with open(vocab_file, "r") as f:
                return json.load(f)

    def __len__(self) -> int:
        return len(self.questions)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """Get a single sample"""
        question_data = self.questions[idx]
        annotation_data = self.annotations[idx]

        # Load image
        image_id = question_data["image_id"]
        image_filename = f"COCO_{self.split}2014_{image_id:012d}.jpg"
        image_path = self.image_dir / image_filename

        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            print(f"Warning: Could not load image {image_path}: {e}")
            # Create a blank image as fallback
            image = Image.new("RGB", (224, 224), color="black")

        # Apply transformations
        if self.transform:
            image = self.transform(image)

        # Get question and answers
        question = question_data["question"]
        answers = annotation_data["answers"]

        # Get most frequent answer
        answer_counts: Dict[str, int] = {}
        for answer_item in answers:
            answer = answer_item["answer"]
            answer_counts[answer] = answer_counts.get(answer, 0) + 1
        most_frequent_answer = max(answer_counts, key=lambda x: answer_counts[x])

        # Get answer label
        answer_label = self.answer_to_label.get(most_frequent_answer, -1)

        # Create answer score vector (for soft labels)
        answer_score_vector = torch.zeros(len(self.answer_to_label))
        for answer, count in answer_counts.items():
            if answer in self.answer_to_label:
                label = self.answer_to_label[answer]
                # Score is min(count/3, 1.0) as per VQA evaluation
                score = min(count / 3.0, 1.0)
                answer_score_vector[label] = score

        sample = {
            "image": image,
            "question": question,
            "answer": most_frequent_answer,
            "answer_label": answer_label,
            "answer_scores": answer_score_vector,
            "question_id": question_data["question_id"],
            "image_id": image_id,
            "question_type": annotation_data.get("question_type", "unknown"),
            "answer_type": annotation_data.get("answer_type", "unknown"),
        }

        # Process with BLIP processor if available
        if self.processor is not None:
            encoding = self.processor(
                images=image,
                text=question,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=config.model.max_text_length,
            )

            # Remove batch dimension
            for key in encoding:
                if isinstance(encoding[key], torch.Tensor):
                    encoding[key] = encoding[key].squeeze(0)

            sample["encoding"] = encoding

        return sample
