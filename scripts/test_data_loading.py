"""
Quick test script to verify data loading works correctly
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models import load_blip_processor
from src.data import create_dataloaders

def test_data_loading():
    """Test that data loading works"""
    print("=" * 60)
    print("Testing Data Loading")
    print("=" * 60)
    print()
    
    # Load processor
    print("[1/3] Loading BLIP processor...")
    processor = load_blip_processor()
    print("[SUCCESS] Processor loaded")
    print()
    
    # Create dataloaders with limited samples
    print("[2/3] Creating dataloaders...")
    print("  Using 100 train samples and 50 test samples for quick test")
    train_loader, val_loader = create_dataloaders(
        processor=processor,
        train_max_samples=100,
        val_max_samples=50,
        use_hf_dataset=True,
        dataset_name="flaviagiammarino/vqa-rad"
    )
    print("[SUCCESS] Dataloaders created")
    print()
    
    # Test loading a batch
    print("[3/3] Testing batch loading...")
    batch = next(iter(train_loader))
    print(f"  Batch keys: {list(batch.keys())}")
    print(f"  Number of samples in batch: {len(batch['questions'])}")
    print(f"  Sample question: {batch['questions'][0]}")
    print(f"  Sample answer: {batch['answers'][0]}")
    print("[SUCCESS] Batch loaded successfully")
    print()
    
    print("=" * 60)
    print("[READY] Data loading test passed!")
    print("=" * 60)
    print()
    print("You're ready to start training!")
    print("Next step: Run the training notebook or training script")
    
    return True

if __name__ == "__main__":
    try:
        test_data_loading()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
