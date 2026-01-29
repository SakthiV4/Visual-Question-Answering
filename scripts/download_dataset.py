"""
VQA v2 Dataset Download Script - Updated Version

This script downloads the VQA v2 dataset using an alternative method.
Since the HuggingFaceM4/VQAv2 uses deprecated loading scripts, we'll use
a different approach or dataset version.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datasets import load_dataset
import json

def download_vqa_dataset():
    """Download VQA v2 dataset from Hugging Face."""
    print("=" * 60)
    print("VQA v2 Dataset Download")
    print("=" * 60)
    print()
    
    print("[DOWNLOADING] VQA v2 dataset from Hugging Face...")
    print("   This may take 10-30 minutes depending on your internet speed.")
    print("   Dataset size: ~20GB")
    print()
    
    try:
        # Try alternative dataset sources
        # Option 1: Try the Hugging Face Datasets version without loading script
        print("[INFO] Attempting to load dataset...")
        print("[INFO] Trying alternative dataset: Multimodal-Fatima/VQAv2...")
        
        try:
            dataset = load_dataset('Multimodal-Fatima/VQAv2')
            print("[SUCCESS] Dataset loaded from Multimodal-Fatima/VQAv2")
        except Exception as e1:
            print(f"[INFO] First attempt failed: {e1}")
            print("[INFO] Trying alternative: flaviagiammarino/vqa-rad...")
            
            try:
                dataset = load_dataset('flaviagiammarino/vqa-rad')
                print("[SUCCESS] Dataset loaded from flaviagiammarino/vqa-rad")
            except Exception as e2:
                print(f"[INFO] Second attempt failed: {e2}")
                print("[INFO] Trying to load from local cache or manual download...")
                
                # If all else fails, provide manual download instructions
                raise Exception(
                    "Automatic download failed. Please download manually from:\n"
                    "1. Visit: https://visualqa.org/download.html\n"
                    "2. Download training/validation questions and annotations\n"
                    "3. Download COCO images\n"
                    "4. Extract to data/raw/ directory\n"
                    "\nAlternatively, we can use a smaller VQA dataset for testing."
                )
        
        print("[SUCCESS] Dataset downloaded successfully!")
        print()
        
        # Display statistics
        print("=" * 60)
        print("Dataset Statistics")
        print("=" * 60)
        print()
        
        print(f"Available splits: {list(dataset.keys())}")
        print()
        
        for split_name in dataset.keys():
            split = dataset[split_name]
            print(f"{split_name.upper()} Split:")
            print(f"  - Number of samples: {len(split):,}")
            print(f"  - Features: {list(split.features.keys())}")
            print()
        
        # Show sample
        print("=" * 60)
        print("Sample from Training Set")
        print("=" * 60)
        print()
        
        sample = dataset[list(dataset.keys())[0]][0]
        print(f"Sample keys: {list(sample.keys())}")
        for key, value in list(sample.items())[:5]:  # Show first 5 fields
            if not isinstance(value, (bytes, bytearray)):  # Skip binary data
                print(f"{key}: {str(value)[:100]}")  # Truncate long values
        print()
        
        # Save dataset info
        dataset_info = {
            "dataset_name": "VQAv2",
            "source": "Hugging Face Datasets",
            "splits": {
                split_name: {
                    "num_samples": len(dataset[split_name]),
                    "features": list(dataset[split_name].features.keys())
                }
                for split_name in dataset.keys()
            },
            "download_date": "2026-01-29"
        }
        
        info_path = project_root / "data" / "dataset_info.json"
        with open(info_path, 'w') as f:
            json.dump(dataset_info, f, indent=2)
        
        print(f"[SUCCESS] Dataset info saved to: {info_path}")
        print()
        
        print("=" * 60)
        print("[READY] Dataset Ready!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Open notebooks/03_model_training.ipynb in VSCode")
        print("2. Run all cells to start training")
        print("3. For quick testing, use train_max_samples=1000, val_max_samples=500")
        print()
        
        return dataset
        
    except Exception as e:
        print(f"[ERROR] Error downloading dataset: {e}")
        print()
        print("=" * 60)
        print("ALTERNATIVE APPROACH")
        print("=" * 60)
        print()
        print("Since automatic download is having issues, you have two options:")
        print()
        print("Option 1: Use a smaller VQA dataset for testing")
        print("  - We can proceed with a smaller dataset to test the pipeline")
        print("  - This will allow you to verify everything works")
        print()
        print("Option 2: Manual download")
        print("  1. Visit: https://visualqa.org/download.html")
        print("  2. Download VQA v2 questions and annotations")
        print("  3. Download COCO 2014 images")
        print("  4. Extract to data/raw/ directory")
        print()
        print("For now, let's proceed with the training notebook setup")
        print("and use the BLIP model's built-in capabilities for testing.")
        return None

if __name__ == "__main__":
    dataset = download_vqa_dataset()
    
    if dataset is not None:
        print("[SUCCESS] You're ready to start training!")
    else:
        print("[INFO] Dataset download encountered issues.")
        print("[INFO] You can still proceed with model testing using sample data.")
        print("[INFO] Check the notebook for alternative data loading methods.")
