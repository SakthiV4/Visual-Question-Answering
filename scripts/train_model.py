"""
VQA Model Training Script

This script trains a BLIP model on the VQA dataset for visually impaired assistance.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import torch
from src.config import config
from src.models import load_blip_model, load_blip_processor
from src.data import create_dataloaders
from src.training import VQATrainer
from src.utils import set_seed, get_device

def main():
    """Main training function"""
    print("=" * 60)
    print("VQA Model Training")
    print("=" * 60)
    print()
    
    # Set random seed
    set_seed(config.seed)
    
    # Get device
    device = get_device()
    
    # Print configuration
    print("Configuration:")
    print(f"  Model: {config.model.model_name}")
    print(f"  Batch size: {config.training.batch_size}")
    print(f"  Epochs: {config.training.num_epochs}")
    print(f"  Learning rate: {config.training.learning_rate}")
    print(f"  Device: {device}")
    print()
    
    # Load processor
    print("[1/4] Loading BLIP processor...")
    processor = load_blip_processor()
    print("[SUCCESS] Processor loaded")
    print()
    
    # Create dataloaders
    print("[2/4] Creating dataloaders...")
    print("  Using full dataset for training")
    train_loader, val_loader = create_dataloaders(
        processor=processor,
        use_hf_dataset=True,
        dataset_name="flaviagiammarino/vqa-rad"
    )
    print("[SUCCESS] Dataloaders created")
    print()
    
    # Initialize model
    print("[3/4] Initializing BLIP model...")
    num_labels = len(train_loader.dataset.answer_to_label)
    print(f"  Number of answer classes: {num_labels}")
    model = load_blip_model(num_labels=num_labels)
    print("[SUCCESS] Model initialized")
    print()
    
    # Initialize trainer
    print("[4/4] Starting training...")
    trainer = VQATrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        answer_to_label=train_loader.dataset.answer_to_label,
        label_to_answer=train_loader.dataset.label_to_answer,
        use_wandb=False  # Set to True to enable Weights & Biases logging
    )
    
    # Train model
    trainer.train()
    
    print()
    print("=" * 60)
    print("[COMPLETE] Training finished!")
    print("=" * 60)
    print()
    print("Outputs:")
    print(f"  - Final model: models/final/")
    print(f"  - Checkpoints: models/checkpoints/")
    print(f"  - Model config: outputs/model_config.json")
    print()
    print("Next steps:")
    print("  1. Review training metrics")
    print("  2. Test model inference")
    print("  3. Follow DEPLOYMENT_GUIDE.md for mobile app development")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Training interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
