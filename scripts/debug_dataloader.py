import sys
from pathlib import Path
import torch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.models import load_blip_processor
from src.data import create_dataloaders

def main():
    print("Initializing debug...")
    config.training.batch_size = 8
    
    print("Loading processor...")
    processor = load_blip_processor()
    
    print("Creating dataloaders...")
    train_loader, _ = create_dataloaders(
        processor=processor,
        train_max_samples=16,
        use_hf_dataset=True,
        dataset_name="flaviagiammarino/vqa-rad"
    )
    
    print(f"Train loader length: {len(train_loader)}")
    
    # Get one batch
    batch = next(iter(train_loader))
    
    if "encoding" in batch:
        encoding = batch["encoding"]
        input_ids = encoding["input_ids"]
        print(f"\ninput_ids shape: {input_ids.shape}")
        
        if "labels" in batch:
            labels = batch["labels"]
            print(f"labels shape: {labels.shape}")
            if labels.dim() == 2:
                print("SUCCESS: labels is 2D (Batch, SeqLen).")
            else:
                print(f"WARNING: labels has unexpected dimensions: {labels.dim()}")
        else:
            print("ERROR: 'labels' key missing in batch")
            
    else:
        print("ERROR: batch has no 'encoding' key")

if __name__ == "__main__":
    main()
