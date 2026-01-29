"""
Utility helper functions
"""

import json
import random
import numpy as np
import torch
from pathlib import Path
from datetime import datetime
from typing import Any, Dict


def set_seed(seed: int = 42):
    """
    Set random seed for reproducibility

    Args:
        seed: Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    print(f"Random seed set to {seed}")


def get_device() -> torch.device:
    """
    Get the best available device (CUDA, MPS, or CPU)

    Returns:
        torch.device
    """
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
        print(
            f"CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
        )
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using MPS (Apple Silicon) device")
    else:
        device = torch.device("cpu")
        print("Using CPU device")

    return device


def save_json(data: Dict[str, Any], filepath: Path):
    """
    Save dictionary to JSON file

    Args:
        data: Dictionary to save
        filepath: Path to save file
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved JSON to {filepath}")


def load_json(filepath: Path) -> Dict[str, Any]:
    """
    Load JSON file

    Args:
        filepath: Path to JSON file

    Returns:
        Loaded dictionary
    """
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def format_time(seconds: float) -> str:
    """
    Format seconds into human-readable time string

    Args:
        seconds: Time in seconds

    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def get_timestamp() -> str:
    """
    Get current timestamp string

    Returns:
        Timestamp in format YYYY-MM-DD_HH-MM-SS
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def count_parameters(model: torch.nn.Module) -> int:
    """
    Count trainable parameters in a model

    Args:
        model: PyTorch model

    Returns:
        Number of trainable parameters
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def get_model_size_mb(model: torch.nn.Module) -> float:
    """
    Get model size in megabytes

    Args:
        model: PyTorch model

    Returns:
        Model size in MB
    """
    param_size = 0
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()

    buffer_size = 0
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()

    size_mb = (param_size + buffer_size) / 1024 / 1024
    return size_mb


def print_model_info(model: torch.nn.Module):
    """
    Print model information

    Args:
        model: PyTorch model
    """
    num_params = count_parameters(model)
    size_mb = get_model_size_mb(model)

    print("=" * 60)
    print("Model Information")
    print("=" * 60)
    print(f"Trainable parameters: {num_params:,}")
    print(f"Model size: {size_mb:.2f} MB")
    print("=" * 60)
