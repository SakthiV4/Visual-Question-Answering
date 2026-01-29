"""
Configuration file for VQA Training Pipeline
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from typing import Tuple, List

# Base Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"
FINAL_MODELS_DIR = MODELS_DIR / "final"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
LOGS_DIR = OUTPUTS_DIR / "logs"
METRICS_DIR = OUTPUTS_DIR / "metrics"

# Create directories if they don't exist
for dir_path in [
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    CHECKPOINTS_DIR,
    FINAL_MODELS_DIR,
    LOGS_DIR,
    METRICS_DIR,
]:
    dir_path.mkdir(parents=True, exist_ok=True)


@dataclass
class ModelConfig:
    """Model configuration parameters"""

    # Model selection
    model_name: str = "Salesforce/blip-vqa-base"
    model_type: str = "blip"

    # Model architecture
    vision_encoder: str = "ViT-B/16"
    text_encoder: str = "BERT-base"
    hidden_size: int = 768
    num_attention_heads: int = 12

    # Image preprocessing
    image_size: Tuple[int, int] = (384, 384)
    image_mean: Tuple[float, float, float] = (0.48145466, 0.4578275, 0.40821073)
    image_std: Tuple[float, float, float] = (0.26862954, 0.26130258, 0.27577711)

    # Text preprocessing
    max_text_length: int = 35
    max_answer_length: int = 10


@dataclass
class DataConfig:
    """Data configuration parameters"""

    dataset_name: str = "vqa_v2"
    train_split: str = "train"
    val_split: str = "validation"
    num_workers: int = 4
    pin_memory: bool = True
    use_augmentation: bool = True
    augmentation_prob: float = 0.5


@dataclass
class TrainingConfig:
    """Training configuration parameters"""

    batch_size: int = 8
    num_epochs: int = 10
    learning_rate: float = 1e-5
    weight_decay: float = 0.01
    warmup_steps: int = 1000
    optimizer: str = "adamw"
    scheduler: str = "linear"
    use_fp16: bool = True
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    eval_steps: int = 500
    save_steps: int = 1000
    logging_steps: int = 100
    early_stopping_patience: int = 3
    target_accuracy: float = 0.80
    device: str = "cuda"


@dataclass
class WandbConfig:
    """Weights & Biases configuration"""

    project_name: str = "vqa-visually-impaired"
    entity: Optional[str] = None
    run_name: Optional[str] = None
    log_model: bool = True
    tags: List[str] = field(default_factory=lambda: ["vqa", "blip", "accessibility"])


@dataclass
class Config:
    """Main configuration class"""

    model: ModelConfig = field(default_factory=ModelConfig)
    data: DataConfig = field(default_factory=DataConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    wandb: WandbConfig = field(default_factory=WandbConfig)
    seed: int = 42
    experiment_name: str = "blip_vqa_v1"

    def to_dict(self):
        """Convert config to dictionary"""
        return {
            "model": self.model.__dict__,
            "data": self.data.__dict__,
            "training": self.training.__dict__,
            "wandb": self.wandb.__dict__,
            "seed": self.seed,
            "experiment_name": self.experiment_name,
        }


# Global config instance
config = Config()
