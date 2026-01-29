"""
Evaluation metrics for VQA
"""

import torch
from typing import Dict, List, Optional
from collections import defaultdict


def compute_vqa_accuracy(
    predictions: List[str], ground_truths: List[List[str]]
) -> float:
    """
    Compute VQA accuracy metric

    VQA accuracy: min(# humans that provided that answer / 3, 1)

    Args:
        predictions: List of predicted answers
        ground_truths: List of lists of ground truth answers

    Returns:
        VQA accuracy score
    """
    assert len(predictions) == len(ground_truths)

    total_score = 0.0
    for pred, gt_list in zip(predictions, ground_truths):
        # Count how many times the prediction appears in ground truth
        count = sum(1 for gt in gt_list if gt == pred)
        # VQA accuracy formula
        score = min(count / 3.0, 1.0)
        total_score += score

    return total_score / len(predictions)


class VQAMetrics:
    """VQA Metrics Tracker"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all metrics"""
        self.predictions = []
        self.ground_truths = []
        self.question_types = defaultdict(lambda: {"correct": 0, "total": 0})
        self.answer_types = defaultdict(lambda: {"correct": 0, "total": 0})
        self.total_loss = 0.0
        self.num_batches = 0

    def update(
        self,
        predictions: List[str],
        ground_truths: List[str],
        question_types: Optional[List[str]] = None,
        answer_types: Optional[List[str]] = None,
        loss: Optional[float] = None,
    ):
        """
        Update metrics with batch results

        Args:
            predictions: Predicted answers
            ground_truths: Ground truth answers
            question_types: Question types (yes/no, number, other)
            answer_types: Answer types
            loss: Batch loss
        """
        self.predictions.extend(predictions)
        self.ground_truths.extend(ground_truths)

        # Track accuracy by question type
        if question_types is not None:
            for pred, gt, qtype in zip(predictions, ground_truths, question_types):
                self.question_types[qtype]["total"] += 1
                if pred == gt:
                    self.question_types[qtype]["correct"] += 1

        # Track accuracy by answer type
        if answer_types is not None:
            for pred, gt, atype in zip(predictions, ground_truths, answer_types):
                self.answer_types[atype]["total"] += 1
                if pred == gt:
                    self.answer_types[atype]["correct"] += 1

        # Track loss
        if loss is not None:
            self.total_loss += loss
            self.num_batches += 1

    def compute(self) -> Dict[str, float]:
        """
        Compute all metrics

        Returns:
            Dictionary of metrics
        """
        # Overall accuracy
        correct = sum(
            1 for pred, gt in zip(self.predictions, self.ground_truths) if pred == gt
        )
        accuracy = correct / len(self.predictions) if self.predictions else 0.0

        # Average loss
        avg_loss = self.total_loss / self.num_batches if self.num_batches > 0 else 0.0

        metrics = {
            "accuracy": accuracy,
            "loss": avg_loss,
            "num_samples": len(self.predictions),
        }

        # Accuracy by question type
        for qtype, stats in self.question_types.items():
            if stats["total"] > 0:
                metrics[f"accuracy_{qtype}"] = stats["correct"] / stats["total"]

        # Accuracy by answer type
        for atype, stats in self.answer_types.items():
            if stats["total"] > 0:
                metrics[f"accuracy_answer_{atype}"] = stats["correct"] / stats["total"]

        return metrics

    def get_summary(self) -> str:
        """Get formatted summary of metrics"""
        metrics = self.compute()

        summary = f"Accuracy: {metrics['accuracy']:.4f}\n"
        summary += f"Loss: {metrics['loss']:.4f}\n"
        summary += f"Samples: {metrics['num_samples']}\n"

        # Question type breakdown
        if any(
            k.startswith("accuracy_") and not k.startswith("accuracy_answer_")
            for k in metrics.keys()
        ):
            summary += "\nBy Question Type:\n"
            for key, value in metrics.items():
                if key.startswith("accuracy_") and not key.startswith(
                    "accuracy_answer_"
                ):
                    qtype = key.replace("accuracy_", "")
                    summary += f"  {qtype}: {value:.4f}\n"

        return summary


def compute_batch_accuracy(logits: torch.Tensor, labels: torch.Tensor) -> float:
    """
    Compute accuracy for a single batch

    Args:
        logits: Model output logits [batch_size, num_classes]
        labels: Ground truth labels [batch_size]

    Returns:
        Batch accuracy
    """
    predictions = torch.argmax(logits, dim=-1)
    correct = (predictions == labels).sum().item()
    accuracy = correct / labels.size(0)
    return accuracy
